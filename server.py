from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request, make_response
from data import db_session
from data.solutions import Solution
from data.users import User
from data.groups import Group
from data.group_members import GroupMember
from form.group_solution import GroupSolutionsForm
from form.user import RegisterForm, LoginForm, GroupForm
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
import uuid
from form.task import TaskForm
from sqlalchemy.orm import joinedload
from configs import TASK_CONFIG, OPERATIONS_CONFIG, route_mapping, ex, secret_key, task_type_names
import os
from werkzeug.utils import secure_filename
from flask import send_from_directory, abort
from data.homeworks import Homework
from data.solution_files import SolutionFile
from form.homework import HomeworkForm

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = secret_key

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

db_session.global_init("db/web.db")

# Конфигурация загрузки файлов
UPLOAD_FOLDER = 'static/uploads'
HOMEWORK_FOLDER = os.path.join(UPLOAD_FOLDER, 'homeworks')
SOLUTION_FOLDER = os.path.join(UPLOAD_FOLDER, 'solutions')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx', 'txt', 'zip', 'rar'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32 MB

# Создаем папки, если их нет
os.makedirs(HOMEWORK_FOLDER, exist_ok=True)
os.makedirs(SOLUTION_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
                  saw_solution, file=None):
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
        db_sess.flush()  # Получаем ID решения

        # Сохраняем файл, если он был загружен
        if file and file.filename:
            filename = secure_filename(file.filename)
            unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}_{filename}"
            filepath = os.path.join(SOLUTION_FOLDER, unique_filename)
            file.save(filepath)

            solution_file = SolutionFile(
                solution_id=solution.id,
                filename=unique_filename,
                original_filename=filename,
                filepath=filepath
            )
            db_sess.add(solution_file)

        if is_correct and not saw_solution:
            member = db_sess.query(GroupMember).filter_by(group_id=group_id, user_id=user_id).first()
            if member:
                member.points += points

        db_sess.commit()
        return solution.id
    except Exception as e:
        print(f"Error saving solution: {e}")
        db_sess.rollback()
        return None
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

    # Получаем файл из формы
    file = form.file.data if form.file.data and form.file.data.filename else None

    save_solution(group_id, current_user.id, task_type_names[task_key], task, user_answer,
                  correct_answer, is_correct, config['points'], saw_solution, file)

    if is_correct or request.args.get('show_solution') == 'true':
        solution_log = config['get_solution'](task)
        show_solution_param = True
    else:
        solution_log = None
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


@app.route('/group/<int:group_id>/solutions', methods=['GET', 'POST'])
@login_required
def group_solutions(group_id):
    db_sess = db_session.create_session()
    try:
        group = db_sess.query(Group).get(group_id)
        if not group:
            flash("Группа не найдена")
            return redirect(url_for('view_groups'))

        # Проверяем, что текущий пользователь - учитель этой группы
        teacher = db_sess.query(GroupMember).filter_by(
            group_id=group_id,
            user_id=current_user.id,
            is_teacher=True
        ).first()
        if not teacher:
            flash("Нет доступа")
            return redirect(url_for('view_groups'))

        form = GroupSolutionsForm()

        # Если это GET-запрос, показываем все решения
        if request.method == 'GET':
            solutions = db_sess.query(Solution).filter_by(group_id=group_id).order_by(
                Solution.submitted_at.desc()).all()
            return render_template('group_solutions.html', group=group, solutions=solutions, form=form)

        # Если это POST-запрос (отправлена форма)
        if form.validate_on_submit():
            # Проверяем, какая кнопка была нажата
            if form.clean.data:  # Кнопка "Очистить историю"
                # Удаляем все решения для этой группы
                db_sess.query(Solution).filter_by(group_id=group_id).delete()
                db_sess.commit()
                flash("История решений очищена", "success")
                return redirect(url_for('group_solutions', group_id=group_id))

            elif form.submit.data or form.show_all.data:  # Кнопки "Найти" или "Показать все"
                # Получаем данные из формы
                searching_surname = form.surname.data.strip() if form.surname.data else None
                searching_name = form.name.data.strip() if form.name.data else None
                searching_patronymic = form.patronymic.data.strip() if form.patronymic.data else None
                searching_date = form.date.data

                # Начинаем с базового запроса
                solutions_query = db_sess.query(Solution).filter_by(group_id=group_id)

                # Если нажата "Показать все" или все поля пустые - показываем все
                if form.show_all.data or not any(
                        [searching_surname, searching_name, searching_patronymic, searching_date]):
                    solutions = solutions_query.order_by(Solution.submitted_at.desc()).all()
                    return render_template('group_solutions.html', group=group, solutions=solutions, form=form)

                # Применяем фильтры
                # Фильтр по дате
                if searching_date:
                    start_date = datetime.combine(searching_date, datetime.min.time())
                    end_date = datetime.combine(searching_date, datetime.max.time())
                    solutions_query = solutions_query.filter(
                        Solution.submitted_at >= start_date,
                        Solution.submitted_at <= end_date
                    )

                # Фильтр по ФИО
                filtered_user_ids = []
                if searching_surname or searching_name or searching_patronymic:
                    # Находим всех учеников группы
                    group_students = db_sess.query(User).join(GroupMember).filter(
                        GroupMember.group_id == group_id,
                        GroupMember.is_teacher == False
                    ).all()

                    # Фильтруем учеников по заданным критериям
                    for student in group_students:
                        match = True

                        if searching_surname:
                            if not student.surname or searching_surname.lower() != student.surname.lower():
                                match = False

                        if searching_name:
                            if not student.name or searching_name.lower() != student.name.lower():
                                match = False

                        if searching_patronymic:
                            if not student.patronymic or searching_patronymic.lower() != student.patronymic.lower():
                                match = False

                        if match:
                            filtered_user_ids.append(student.id)

                # Если есть фильтры по ФИО, применяем их
                if filtered_user_ids:
                    solutions_query = solutions_query.filter(Solution.user_id.in_(filtered_user_ids))
                elif searching_surname or searching_name or searching_patronymic:
                    # Если указаны критерии ФИО, но никто не найден - возвращаем пустой список
                    solutions = []
                    return render_template('group_solutions.html', group=group, solutions=solutions, form=form)

                # Получаем результаты
                solutions = solutions_query.order_by(Solution.submitted_at.desc()).all()

                return render_template('group_solutions.html', group=group, solutions=solutions, form=form)

        # Если форма не прошла валидацию
        solutions = db_sess.query(Solution).filter_by(group_id=group_id).order_by(Solution.submitted_at.desc()).all()
        return render_template('group_solutions.html', group=group, solutions=solutions, form=form)

    except Exception as e:
        print(f"Ошибка в group_solutions: {e}")
        flash(f"Произошла ошибка: {e}", "error")
        return redirect(url_for('view_group', group_id=group_id))
    finally:
        db_sess.close()


# Маршруты для домашних заданий
@app.route('/group/<int:group_id>/homeworks')
@login_required
def group_homeworks(group_id):
    """Просмотр домашних заданий группы"""
    db_sess = db_session.create_session()
    try:
        group = db_sess.query(Group).get(group_id)

        if not group:
            abort(404)

        # Проверка доступа
        teacher = db_sess.query(GroupMember).filter_by(
            group_id=group_id,
            user_id=current_user.id,
            is_teacher=True
        ).first()

        # Проверяем, является ли пользователь участником группы или учителем
        if not any([current_user.id == member.user_id for member in group.members]) \
                and not teacher:
            abort(403)

        homeworks = db_sess.query(Homework).filter_by(group_id=group_id).order_by(Homework.created_at.desc()).all()

        return render_template('group_homeworks.html',
                               group=group,
                               homeworks=homeworks,
                               is_teacher=bool(teacher))
    finally:
        db_sess.close()


@app.route('/group/<int:group_id>/upload_homework', methods=['GET', 'POST'])
@login_required
def upload_homework(group_id):
    """Загрузка домашнего задания (только для учителей)"""
    db_sess = db_session.create_session()
    try:
        # Проверяем, является ли пользователь учителем в этой группе
        teacher = db_sess.query(GroupMember).filter_by(
            group_id=group_id,
            user_id=current_user.id,
            is_teacher=True
        ).first()

        if not teacher:
            abort(403)

        group = db_sess.query(Group).get(group_id)

        if not group:
            abort(404)

        form = HomeworkForm()

        if form.validate_on_submit():
            file = form.file.data

            if file and allowed_file(file.filename):
                # Генерируем уникальное имя файла
                filename = secure_filename(file.filename)
                unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{current_user.id}_{filename}"
                filepath = os.path.join(HOMEWORK_FOLDER, unique_filename)

                # Сохраняем файл
                file.save(filepath)

                # Сохраняем информацию в БД
                homework = Homework(
                    group_id=group_id,
                    user_id=current_user.id,
                    filename=unique_filename,
                    original_filename=filename,
                    filepath=filepath,
                    description=form.description.data
                )

                db_sess.add(homework)
                db_sess.commit()

                flash('Задание успешно добавлено!', 'success')
                return redirect(url_for('group_homeworks', group_id=group_id))
            else:
                flash('Недопустимый формат файла', 'danger')

        return render_template('upload_homework.html', form=form, group=group)
    finally:
        db_sess.close()


@app.route('/homework/<int:homework_id>/download')
@login_required
def download_homework(homework_id):
    """Скачивание домашнего задания"""
    db_sess = db_session.create_session()
    try:
        homework = db_sess.query(Homework).get(homework_id)

        if not homework:
            abort(404)

        # Проверка доступа
        group = homework.group
        if not any([current_user.id == member.user_id for member in group.members]) \
                and not db_sess.query(GroupMember).filter_by(
            group_id=group.id,
            user_id=current_user.id,
            is_teacher=True
        ).first():
            abort(403)

        # Отправляем файл
        try:
            return send_from_directory(
                HOMEWORK_FOLDER,
                homework.filename,
                as_attachment=True,
                download_name=homework.original_filename
            )
        except FileNotFoundError:
            flash('Файл не найден', 'danger')
            return redirect(url_for('group_homeworks', group_id=homework.group_id))
    finally:
        db_sess.close()


@app.route('/homework/<int:homework_id>/delete', methods=['POST'])
@login_required
def delete_homework(homework_id):
    """Удаление домашнего задания (только учитель, который добавил)"""
    db_sess = db_session.create_session()
    try:
        homework = db_sess.query(Homework).get(homework_id)

        if not homework:
            abort(404)

        # Проверяем, является ли пользователь учителем, который добавил задание
        if current_user.id != homework.user_id:
            abort(403)

        # Удаляем файл
        try:
            os.remove(homework.filepath)
        except:
            pass

        # Удаляем запись из БД
        group_id = homework.group_id
        db_sess.delete(homework)
        db_sess.commit()

        flash('Задание удалено', 'success')
        return redirect(url_for('group_homeworks', group_id=group_id))
    finally:
        db_sess.close()


@app.route('/solution_file/<int:file_id>/download')
@login_required
def download_solution_file(file_id):
    """Скачивание файла решения"""
    db_sess = db_session.create_session()
    try:
        solution_file = db_sess.query(SolutionFile).get(file_id)

        if not solution_file:
            abort(404)

        solution = solution_file.solution

        # Проверка доступа
        # Учитель группы или сам ученик
        teacher = db_sess.query(GroupMember).filter_by(
            group_id=solution.group_id,
            user_id=current_user.id,
            is_teacher=True
        ).first()

        if not teacher and current_user.id != solution.user_id:
            abort(403)

        # Отправляем файл
        try:
            return send_from_directory(
                SOLUTION_FOLDER,
                solution_file.filename,
                as_attachment=True,
                download_name=solution_file.original_filename
            )
        except FileNotFoundError:
            flash('Файл не найден', 'danger')
            return redirect(url_for('group_solutions', group_id=solution.group_id))
    finally:
        db_sess.close()


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
def index():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    return render_template('landing.html')  # Показываем лендинг неавторизованным


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
