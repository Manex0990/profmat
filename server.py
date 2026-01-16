from flask import Flask, render_template, redirect, url_for, flash, request, make_response
from data import db_session
from data.solutions import Solution
from data.users import User
from data.groups import Group
from data.group_members import GroupMember
from form.user import RegisterForm, LoginForm, GroupForm
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
import uuid
from form.task import TaskForm
from sqlalchemy.orm import joinedload
from werkzeug.utils import secure_filename
import os
from configs import TASK_CONFIG, OPERATIONS_CONFIG, route_mapping, ex, secret_key, task_type_names

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = secret_key

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

db_session.global_init("db/web.db")

# Генерация функций для примеров
for operation, config in OPERATIONS_CONFIG.items():
    for level in range(1, 4):
        key = f'{operation}_{level}'
        TASK_CONFIG[key] = {
            'name': f'{config["name"]} ({["простой", "средний", "сложный"][level - 1]})',
            'generate_func': getattr(ex, f'generate_{operation}_stage_{level}'),
            'check_func': ex.check_answer_for_all_stages,
            'points': config['points'][level - 1],
            'get_solution': lambda task, op=operation:
            [f'Просто {["сложим", "вычтем", "перемножим", "разделим"][["sum", "min", "mul", "crop"].index(op)]} все коэффициенты',
             f'Ответ: {ex.answer_for_all_stages(task)}']}


def save_solution(group_id, user_id, task_type, task_content, user_answer, correct_answer, is_correct, points,
                  saw_solution):
    db_sess = db_session.create_session()
    try:
        solution = Solution(
            task_type=task_type,
            task_content=task_content,
            user_answer=user_answer,
            correct_answer=correct_answer,
            is_correct=is_correct,
            points_awarded=points if is_correct and not saw_solution else 0,
            user_id=user_id,
            group_id=group_id
        )
        db_sess.add(solution)

        if is_correct and not saw_solution:
            member = db_sess.query(GroupMember).filter_by(group_id=group_id, user_id=user_id).first()
            if member:
                member.points += points

        db_sess.commit()
    except Exception as e:
        print(f"Error saving solution: {e}")
        db_sess.rollback()
    finally:
        db_sess.close()


def update_points(group_id, user_id, points):
    """Обновление баллов пользователя"""
    db_sess = db_session.create_session()
    try:
        member = db_sess.query(GroupMember).filter_by(group_id=group_id, user_id=user_id).first()
        if member:
            member.points += points
            db_sess.commit()
    finally:
        db_sess.close()


def validate_group_access(group_id):
    """Проверка доступа пользователя к группе"""
    db_sess = db_session.create_session()
    try:
        group = db_sess.query(Group).filter(Group.id == group_id).first()
        if not group:
            flash("Группа не найдена", "error")
            return None, None

        group_member = db_sess.query(GroupMember).filter_by(user_id=current_user.id, group_id=group_id).first()
        if not group_member:
            flash("Вы не состоите в этой группе!", "error")
            return None, None

        return group, group_member
    finally:
        db_sess.close()


def handle_task_request(group_id, task_key, cookie_name, show_solution=False, template_name='task_opened.html'):
    """Универсальный обработчик для всех типов задач"""
    group, group_member = validate_group_access(group_id)
    if not group:
        return redirect(url_for('student_groups'))

    config = TASK_CONFIG[task_key]
    points = config['points']
    task = str(request.cookies.get(cookie_name, config['generate_func']()))
    form = TaskForm()

    # Обработка запроса на показ решения
    show_solution_param = request.args.get('show_solution') == 'true' or show_solution

    if request.method == 'GET':
        solution_log = None
        message = ''

        if show_solution_param:
            solution_log = config['get_solution'](task)
            message = 'Решение показано'

        response = make_response(
            render_template(template_name, title=config['name'], group=group, task=task, form=form,
                            points=points, solution_log=solution_log, show_solution=show_solution_param,
                            task_key=task_key, message=message))
        response.set_cookie(cookie_name, value=str(task), max_age=60 * 60 * 24 * 365 * 2)
        return response

    # POST запрос
    user_answer = form.answer.data
    verdict = config['check_func'](task, user_answer)
    message, is_correct, eq_type, correct_answer = verdict
    saw_solution = request.cookies.get('solution') == '1'
    save_solution(group_id, current_user.id, task_type_names[task_key], task, user_answer, correct_answer, is_correct,
                  config['points'],
                  saw_solution)

    if is_correct or request.args.get('show_solution') == 'true':
        solution_log = config['get_solution'](task)
        show_solution_param = True  # Показываем решение после правильного ответа
    else:
        solution_log = None
        # Даже при неправильном ответе можем показать решение, если был запрос
        if request.args.get('show_solution') == 'true':
            solution_log = config['get_solution'](task)
            show_solution_param = True

    response = make_response(render_template(template_name, title=config['name'], group=group, task=task,
                                             form=form, solution_log=solution_log, message=verdict[0], points=points,
                                             show_solution=show_solution_param, task_key=task_key))

    if verdict[1]:
        response.set_cookie(cookie_name, '', max_age=0)

    return response


@app.route('/student_groups/<int:group_id>/task/linear_inequation', methods=['GET', 'POST'])
@login_required
def open_task_linear_inequation(group_id):
    show_solution = request.args.get('show_solution') == 'true'
    return handle_task_request(group_id, 'linear_inequation', 'cur_task_linear_inequation', show_solution)


@app.route('/student_groups/<int:group_id>/task/module_equation', methods=['GET', 'POST'])
@login_required
def open_task_module_equation(group_id):
    show_solution = request.args.get('show_solution') == 'true'
    return handle_task_request(group_id, 'module_equation', 'cur_task_module_equation', show_solution)


@app.route('/student_groups/<int:group_id>/task/irrational_equation', methods=['GET', 'POST'])
@login_required
def open_task_irrational_equation(group_id):
    show_solution = request.args.get('show_solution') == 'true'
    return handle_task_request(group_id, 'irrational_equation', 'cur_task_irrational_equation', show_solution)


@app.route('/student_groups/<int:group_id>/task/biquadratic_equation', methods=['GET', 'POST'])
@login_required
def open_task_biquadratic_equation(group_id):
    show_solution = request.args.get('show_solution') == 'true'
    return handle_task_request(group_id, 'biquadratic_equation', 'cur_task_biquadratic_equation', show_solution)


@app.route('/student_groups/<int:group_id>/task/quadratic_equation', methods=['GET', 'POST'])
@login_required
def open_task_quadratic_equation(group_id):
    show_solution = request.args.get('show_solution') == 'true'
    return handle_task_request(group_id, 'quadratic_equation', 'cur_task_quadratic_equation', show_solution)


@app.route('/student_groups/<int:group_id>/task/linear_equation', methods=['GET', 'POST'])
@login_required
def open_task_linear_equation(group_id):
    show_solution = request.args.get('show_solution') == 'true'
    return handle_task_request(group_id, 'linear_equation', 'cur_task_linear_equation', show_solution)


@app.route('/student_groups/<int:group_id>/task/<operation>/<int:level>', methods=['GET', 'POST'])
@login_required
def open_task_example(group_id, operation, level):
    task_key = f'{operation}_{level}'
    show_solution = request.args.get('show_solution') == 'true'
    return handle_task_request(group_id, task_key, 'cur_task_operation', show_solution)


@app.route('/student_groups/<int:group_id>/task', methods=['GET', 'POST'])
def open_task_menu(group_id):
    db_sess = db_session.create_session()
    try:
        group, group_member = validate_group_access(group_id)
        if not group:
            return redirect(url_for('student_groups'))

        res = make_response(render_template('task_window.html', group=group))
        # Сбрасываем значения ключей cookie
        res.set_cookie('solution', '0', max_age=60 * 60 * 24 * 365 * 2)
        res.set_cookie('cur_task_biquadratic_equation', '', max_age=0)
        res.set_cookie('cur_task_quadratic_equation', '', max_age=0)
        res.set_cookie('cur_task_linear_equation', '', max_age=0)
        res.set_cookie('cur_task_irrational_equation', '', max_age=0)
        res.set_cookie('cur_task_module_equation', '', max_age=0)
        res.set_cookie('cur_task_linear_inequation', '', max_age=0)
        return res
    finally:
        db_sess.close()


@app.route('/student_groups/<int:group_id>/task/<task_type>/show_solution')
@login_required
def show_solution(group_id, task_type):
    """Показать решение задачи без проверки ответа"""
    # Устанавливаем значение ключа solution в 1 при открытии страницы решения, так как пользователь видел решение
    response = redirect(url_for(route_mapping[task_type], group_id=group_id, show_solution='true'))
    response.set_cookie('solution', '1', max_age=60 * 60 * 24 * 365 * 2)
    return response


@app.route('/group/<int:group_id>/solutions')
@login_required
def group_solutions(group_id):
    db_sess = db_session.create_session()
    group = db_sess.query(Group).get(group_id)
    if not group:
        flash("Группа не найдена")
        return redirect(url_for('view_groups'))

    # Проверяем, что текущий пользователь - учитель этой группы
    teacher = db_sess.query(GroupMember).filter_by(group_id=group_id, user_id=current_user.id, is_teacher=True).first()
    if not teacher:
        flash("Нет доступа")
        return redirect(url_for('view_groups'))

    # Получаем все решения для этой группы, отсортированные по дате
    solutions = db_sess.query(Solution).filter_by(group_id=group_id).order_by(Solution.submitted_at.desc()).all()

    return render_template('group_solutions.html', group=group, solutions=solutions)


@app.route('/student_groups/<int:group_id>/task/<name>', methods=['GET', 'POST'])
def open_change_level_window(group_id, name):
    db_sess = db_session.create_session()
    try:
        group, group_member = validate_group_access(group_id)
        if not group:
            return redirect(url_for('student_groups'))

        res = make_response(render_template('change_level_window.html', group=group, name=name))
        res.set_cookie('cur_task_operation', '', max_age=0)
        return res
    finally:
        db_sess.close()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    try:
        user = db_sess.get(User, user_id)
        return user
    finally:
        db_sess.close()


@app.route('/')
@login_required
def index():
    return render_template('base.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', form=form, message="Пароли не совпадают")

        db_sess = db_session.create_session()
        try:
            if db_sess.query(User).filter(User.email == form.email.data).first():
                return render_template('register.html', form=form, message="Такой пользователь уже есть")

            user = User(surname=form.surname.data,
                        name=form.name.data,
                        patronymic=form.patronymic.data,
                        email=form.email.data,
                        hashed_password=form.password.data,
                        teacher=form.teacher.data)
            user.set_password(form.password.data)
            db_sess.add(user)
            db_sess.commit()
            return redirect('/login')
        except Exception as e:
            print(f"An error occurred during registration: {e}")
            flash("Ошибка при регистрации", "error")
            return render_template('register.html', form=form, message="Ошибка при регистрации")
        finally:
            db_sess.close()
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        try:
            user = db_sess.query(User).filter(User.email == form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                return redirect('/')
            return render_template('login.html', message="Неверный логин или пароль", form=form)
        finally:
            db_sess.close()
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/group/create', methods=['GET', 'POST'])
@login_required
def group_create():
    if not current_user.teacher:
        flash("Нет прав для создания группы")
        return redirect('/')
    form = GroupForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        try:
            group = Group(name=form.name.data)
            db_sess.add(group)
            db_sess.commit()
            teacher_entry = GroupMember(group_id=group.id, user_id=current_user.id, is_teacher=True)
            db_sess.add(teacher_entry)
            db_sess.commit()
            return redirect(url_for('view_group', group_id=group.id))
        finally:
            db_sess.close()
    return render_template('group_create.html', form=form)


@app.route('/group/join/<invite_link>')
@login_required
def join_group(invite_link):
    db_sess = db_session.create_session()
    try:
        group = db_sess.query(Group).filter(Group.invite_link == invite_link).first()
        if not group:
            return render_template('base.html', title='Такой группы нет')

        exists = db_sess.query(GroupMember).filter(GroupMember.group_id == group.id,
                                                   GroupMember.user_id == current_user.id).first()

        is_teacher = db_sess.query(GroupMember).filter_by(group_id=group.id, user_id=current_user.id,
                                                          is_teacher=True).first()
        if is_teacher:
            return redirect(url_for('view_group', group_id=group.id))

        if exists:
            return redirect(url_for('view_student_group', group_id=group.id))

        new_member = GroupMember(group_id=group.id, user_id=current_user.id, is_teacher=False)
        db_sess.add(new_member)
        db_sess.commit()
        return redirect(url_for('view_student_group', group_id=group.id))
    finally:
        db_sess.close()


@app.route('/group/<int:group_id>')
@login_required
def view_group(group_id):
    db_sess = db_session.create_session()
    try:
        group = db_sess.query(Group).filter(Group.id == group_id).first()
        if not group:
            return render_template('base.html', title='Группа не найдена')

        teacher = db_sess.query(GroupMember).filter_by(
            group_id=group_id,
            user_id=current_user.id,
            is_teacher=True
        ).first()

        if not teacher:
            return render_template('base.html', title='Нет доступа')

        members = db_sess.query(GroupMember).options(joinedload(GroupMember.user)).filter_by(group_id=group_id).all()
        return render_template('group_details.html', group=group, members=members)
    finally:
        db_sess.close()


@app.route('/group/<int:group_id>/remove/<int:user_id>', methods=['POST'])
@login_required
def remove_member(group_id, user_id):
    db_sess = db_session.create_session()
    try:
        if not current_user.teacher:
            return render_template('base.html', title='Нет прав')
        member = db_sess.query(GroupMember).filter_by(group_id=group_id, user_id=user_id).first()
        if member:
            db_sess.delete(member)
            db_sess.commit()
        return redirect(url_for('view_group', group_id=group_id))
    finally:
        db_sess.close()


@app.route('/group/<int:group_id>/points/<int:user_id>', methods=['POST'])
@login_required
def add_points(group_id, user_id):
    db_sess = db_session.create_session()
    try:
        if not current_user.teacher:
            return render_template('base.html', title='Нет прав')
        points = int(request.form.get('points', 0))
        member = db_sess.query(GroupMember).filter_by(group_id=group_id, user_id=user_id).first()
        if member:
            member.points += points
            db_sess.commit()
        return redirect(url_for('view_group', group_id=group_id))
    finally:
        db_sess.close()


@app.route('/group/<int:group_id>/regenerate_link', methods=['POST'])
@login_required
def regenerate_invite_link(group_id):
    db_sess = db_session.create_session()
    try:
        group = db_sess.query(Group).filter(Group.id == group_id).first()
        if not group:
            return render_template('base.html', title='Группа не найдена')
        group.invite_link = str(uuid.uuid4())
        db_sess.commit()
        return redirect(url_for('view_group', group_id=group.id))
    finally:
        db_sess.close()


@app.route('/student_groups/<int:group_id>')
@login_required
def view_student_group(group_id):
    db_sess = db_session.create_session()
    try:
        member = db_sess.query(GroupMember).filter_by(group_id=group_id, user_id=current_user.id).first()
        if not member:
            return render_template('base.html', title='Нет доступа')
        group = db_sess.query(Group).filter(Group.id == group_id).first()
        members = db_sess.query(GroupMember).filter(GroupMember.group_id == group_id).all()
        return render_template('student_group_details.html', group=group, members=members)
    finally:
        db_sess.close()


@app.route('/groups')
@login_required
def view_groups():
    db_sess = db_session.create_session()
    try:
        teacher_memberships = db_sess.query(GroupMember).filter_by(user_id=current_user.id, is_teacher=True).all()
        group_ids = [i.group_id for i in teacher_memberships]

        groups = db_sess.query(Group).filter(Group.id.in_(group_ids)).all()

        return render_template('groups.html', groups=groups, title='Мои группы')
    finally:
        db_sess.close()


@app.route('/student_groups')
@login_required
def student_groups():
    if current_user.teacher:
        return render_template('student_groups.html', title='Нет доступа')

    db_sess = db_session.create_session()
    try:
        student_memberships = db_sess.query(GroupMember).filter_by(user_id=current_user.id, is_teacher=False).all()
        group_ids = [i.group_id for i in student_memberships]

        groups = db_sess.query(Group).filter(Group.id.in_(group_ids)).all()

        return render_template('student_groups.html', groups=groups, title='Мои группы')
    finally:
        db_sess.close()


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)


@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        file = request.files.get('avatar')
        if file and file.filename:
            filename = secure_filename(file.filename)
            filepath = os.path.join('static', 'avatars', filename)
            file.save(filepath)

            db_sess = db_session.create_session()
            user = db_sess.get(User, current_user.id)
            user.avatar = f'/static/avatars/{filename}'
            db_sess.commit()
            db_sess.close()

        return redirect(url_for('profile'))

    return render_template('edit_profile.html')


def main():
    app.run()


if __name__ == '__main__':
    main()
