from flask import Flask, render_template, redirect, url_for, flash, request, make_response
from data import db_session
from data.users import User
from data.groups import Group
from data.group_members import GroupMember
from form.user import RegisterForm, LoginForm, GroupForm
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
import uuid
from form.task import TaskForm
from maths import MyMath
from sqlalchemy.orm import joinedload
from werkzeug.utils import secure_filename
import os

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

db_session.global_init("db/web.db")
ex = MyMath()
names = {'square': 'Квадратное уравнение',
         'line': 'Линейное уравнение',
         'sum_1': 'Пример на сложение (простой)',
         'sum_2': 'Пример на сложение (средний)',
         'sum_3': 'Пример на сложение (сложный)',
         'min_1': 'Пример на вычитание (простой)',
         'min_2': 'Пример на вычитание (средний)',
         'min_3': 'Пример на вычитание (сложный)',
         'mul_1': 'Пример на умножение (простой)',
         'mul_2': 'Пример на умножение (средний)',
         'mul_3': 'Пример на умножение (сложный)',
         'crop_1': 'Пример на деление (простой)',
         'crop_2': 'Пример на деление (средний)',
         'crop_3': 'Пример на деление (сложный)'}
funcs = {'Квадратное уравнение': [ex.generate_square_x, ex.check_answer_square_x],
         'Линейное уравнение': [ex.generate_line_x, ex.check_answer_line_x],
         'Пример на сложение (простой)': [ex.generate_sum_stage_1, ex.check_answer_for_all_stages],
         'Пример на сложение (средний)': [ex.generate_sum_stage_2, ex.check_answer_for_all_stages],
         'Пример на сложение (сложный)': [ex.generate_sum_stage_3, ex.check_answer_for_all_stages],
         'Пример на вычитание (простой)': [ex.generate_min_stage_1, ex.check_answer_for_all_stages],
         'Пример на вычитание (средний)': [ex.generate_min_stage_2, ex.check_answer_for_all_stages],
         'Пример на вычитание (сложный)': [ex.generate_min_stage_3, ex.check_answer_for_all_stages],
         'Пример на умножение (простой)': [ex.generate_multiply_stage_1, ex.check_answer_for_all_stages],
         'Пример на умножение (средний)': [ex.generate_multiply_stage_2, ex.check_answer_for_all_stages],
         'Пример на умножение (сложный)': [ex.generate_multiply_stage_3, ex.check_answer_for_all_stages],
         'Пример на деление (простой)': [ex.generate_crop_stage_1, ex.check_answer_for_all_stages],
         'Пример на деление (средний)': [ex.generate_crop_stage_2, ex.check_answer_for_all_stages],
         'Пример на деление (сложный)': [ex.generate_crop_stage_3, ex.check_answer_for_all_stages]}


def update_points(group_id, user_id, points):
    db_sess = db_session.create_session()
    try:
        member = db_sess.query(GroupMember).filter_by(group_id=group_id, user_id=user_id).first()
        if member:
            member.points += points
            db_sess.commit()
    finally:
        db_sess.close()


@app.route('/student_groups/<int:group_id>/task/square', methods=['GET', 'POST'])
@login_required
def open_task_square(group_id):
    db_sess = db_session.create_session()
    try:
        group = db_sess.query(Group).filter(Group.id == group_id).first()
        if not group:
            flash("Группа не найдена", "error")
            return redirect(url_for('student_groups'))

        group_member = db_sess.query(GroupMember).filter_by(user_id=current_user.id, group_id=group_id).first()

        if not group_member:
            flash("Вы не состоите в этой группе!", "error")
            return redirect(url_for('student_groups'))

        task = str(request.cookies.get('cur_task_square', funcs[names['square']][0]()))
        form = TaskForm()
        title_html = names['square']
        page = make_response(render_template('task_opened.html', title=title_html, group=group,
                                             task=task, form=form))
        page.set_cookie('cur_task_square', value=str(task), max_age=60 * 60 * 24 * 365 * 2)
        solution_generation = ['Сначала найдем дискриминант квадратного уравнения:',
                               'Если дискриманант больше нуля, то будет 2 корня',
                               'Если равен нулю, то будет 1 корень',
                               'Если меньше нуля, то Корней нет.',
                               f'D = b\u00B2 - 4ac; D = {ex.find_discriminant(task)}',
                               'Теперь можно найти корни(корень) уравнения',
                               'x1 = (-b - \u221AD) / 2a',
                               'x2 = (-b + \u221AD) / 2a',
                               f'Ответ: {ex.answer_square_x(task)}']
        if request.method == 'POST':
            user_answer = form.answer.data
            verdict = funcs[names['square']][1](task, user_answer)
            if verdict[1]:
                update_points(group_id, current_user.id, 20)
                res = make_response(
                    render_template('task_opened.html', title=title_html, task=task, group=group,
                                    form=form, solution_log=solution_generation, message=verdict[0]))
                res.set_cookie('cur_task_square', '', max_age=0)
            else:
                res = make_response(
                    render_template('task_opened.html', title=title_html, task=task, group=group,
                                    form=form, solution_log=['Дайте верный ответ, чтобы получить решение.'],
                                    message=verdict[0]))
            return res
        return page
    finally:
        db_sess.close()


@app.route('/student_groups/<int:group_id>/task/line', methods=['GET', 'POST'])
@login_required
def open_task_line(group_id):
    db_sess = db_session.create_session()
    try:
        group = db_sess.query(Group).filter(Group.id == group_id).first()

        if not group:
            flash("Группа не найдена", "error")
            return redirect(url_for('student_groups'))

        group_member = db_sess.query(GroupMember).filter_by(user_id=current_user.id, group_id=group_id).first()
        if not group_member:
            flash("Вы не состоите в этой группе!", "error")
            return redirect(url_for('student_groups'))

        task = str(request.cookies.get('cur_task_line', funcs[names['line']][0]()))
        form = TaskForm()
        title_html = names['line']
        page = make_response(render_template('task_opened.html', title=title_html, group=group,
                                             task=task, form=form))
        page.set_cookie('cur_task_line', value=str(task), max_age=60 * 60 * 24 * 365 * 2)
        solution_generation = ['Для того, чтобы решить линейное уравнение нужно все коэффициенты с "х"',
                               'перенести в одну часть уравнения, а остальные в другую.',
                               f'Ответ: {ex.answer_line_x(task)}']
        if request.method == 'POST':
            user_answer = form.answer.data
            verdict = funcs[names['line']][1](task, user_answer)
            if verdict[1]:
                update_points(group_id, current_user.id, 15)
                res = make_response(
                    render_template('task_opened.html', title=title_html, task=task, group=group,
                                    form=form, solution_log=solution_generation, message=verdict[0]))
                res.set_cookie('cur_task_line', '', max_age=0)
            else:
                res = make_response(
                    render_template('task_opened.html', title=title_html, task=task, group=group,
                                    form=form, solution_log=['Дайте верный ответ, чтобы получить решение.'],
                                    message=verdict[0]))
            return res
        return page
    finally:
        db_sess.close()


@app.route('/student_groups/<int:group_id>/task/<title>/<level>', methods=['GET', 'POST'])
@login_required
def open_task_examples_all_stages(group_id, title, level):
    points_data = {'sum_1': 5, 'sum_2': 8, 'sum_3': 10, 'min_1': 5, 'min_2': 8,
                   'min_3': 10, 'mul_1': 7, 'mul_2': 10,
                   'mul_3': 12, 'crop_1': 10, 'crop_2': 12, 'crop_3': 15}
    db_sess = db_session.create_session()
    try:
        group = db_sess.query(Group).filter(Group.id == group_id).first()

        if not group:
            flash("Группа не найдена", "error")
            return redirect(url_for('student_groups'))

        group_member = db_sess.query(GroupMember).filter_by(user_id=current_user.id, group_id=group_id).first()
        if not group_member:
            flash("Вы не состоите в этой группе!", "error")
            return redirect(url_for('student_groups'))

        full_name = '_'.join([title, level])
        task = str(request.cookies.get('cur_task_ex', funcs[names[full_name]][0]()))
        form = TaskForm()
        title_html = names[full_name]
        page = make_response(render_template('task_opened.html', title=title_html, group=group,
                                             task=task, form=form))
        page.set_cookie('cur_task_ex', value=str(task), max_age=60 * 60 * 24 * 365 * 2)
        solution_generation = {'Пример на сложение': ['Просто сложим все коэффициенты',
                                                      f'Ответ: {ex.answer_for_all_stages(task)}'],
                               'Пример на вычитание': ['Просто вычтем все коэффициенты',
                                                       f'Ответ: {ex.answer_for_all_stages(task)}'],
                               'Пример на умножение': ['Просто перемножим все коэффициенты',
                                                       f'Ответ: {ex.answer_for_all_stages(task)}'],
                               'Пример на деление': ['Просто разделим по порядку все коэффициенты',
                                                     f'Ответ: {ex.answer_for_all_stages(task)}']}
        if request.method == 'POST':
            user_answer = form.answer.data
            verdict = funcs[names[full_name]][1](task, user_answer)
            if verdict[1]:
                update_points(group_id, current_user.id, points_data[full_name])
                res = make_response(
                    render_template('task_opened.html', title=title_html, task=task, form=form, group=group,
                                    solution_log=solution_generation[title_html[:-10]], message=verdict[0]))
                res.set_cookie('cur_task_ex', '', max_age=0)
            else:
                res = make_response(
                    render_template('task_opened.html', title=title_html, task=task, group=group,
                                    form=form, solution_log=['Дайте верный ответ, чтобы получить решение.'],
                                    message=verdict[0]))
            return res
        return page
    finally:
        db_sess.close()


# возможен баг с проверкой примеров из-за (не 5 а 5.0)
@app.route('/student_groups/<int:group_id>/task', methods=['GET', 'POST'])
def open_task_menu(group_id):
    db_sess = db_session.create_session()
    try:
        group = db_sess.query(Group).filter(Group.id == group_id).first()

        if not group:
            flash("Группа не найдена", "error")
            return redirect(url_for('student_groups'))

        group_member = db_sess.query(GroupMember).filter_by(user_id=current_user.id, group_id=group_id).first()
        if not group_member:
            flash("Вы не состоите в этой группе!", "error")
            return redirect(url_for('student_groups'))
        res = make_response(render_template('task_window.html', group=group))
        res.set_cookie('cur_task_square', '', max_age=0)
        res.set_cookie('cur_task_line', '', max_age=0)
        return res
    finally:
        db_sess.close()


@app.route('/student_groups/<int:group_id>/task/<name>', methods=['GET', 'POST'])
def open_change_level_window(group_id, name):
    db_sess = db_session.create_session()
    try:
        group = db_sess.query(Group).filter(Group.id == group_id).first()

        if not group:
            flash("Группа не найдена", "error")
            return redirect(url_for('student_groups'))

        group_member = db_sess.query(GroupMember).filter_by(user_id=current_user.id, group_id=group_id).first()
        if not group_member:
            flash("Вы не состоите в этой группе!", "error")
            return redirect(url_for('student_groups'))
        res = make_response(render_template('change_level_window.html', group=group, name=name))
        res.set_cookie('cur_task_ex', '', max_age=0)
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
    if not current_user.teacher:
        return render_template('student_groups.html',
                               line='Вы не учитель, у вас нет ваших групп. Перейдите в раздел Мои группы.')

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