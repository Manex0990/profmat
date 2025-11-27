from maths import MyMath

ex = MyMath()


# Функция для вычисления и округления корней
def calculate_and_round_roots(root_str):
    """Вычисляет числовое значение корня и округляет до сотых"""
    try:
        # Если корень в формате √number
        if '√' in root_str:
            number_str = root_str.replace('√', '').replace('-', '')
            number = float(number_str)
            result = number ** 0.5
            if root_str.startswith('-'):
                result = -result
            return round(result, 2)
        # Если это просто число
        else:
            return round(float(root_str), 2)
    except:
        return root_str


def get_biquadratic_solution(task):
    """
    Функция для получения пошагового решения биквадратного уравнения
    """
    steps = []

    # Шаг 1: Замена переменной
    steps.append('1. Сделаем замену переменной: y = x²')
    equation_y = task.replace('x⁴', 'y²').replace('x²', 'y')
    steps.append(f'   Получим: {equation_y}')

    # Находим коэффициенты квадратного уравнения
    try:
        a, b, c = ex.find_coofs_quadratic_equation(task.replace('x²', 'x').replace('x⁴', 'x²'))
        D = ex.find_discriminant_biquadratic(task)

        steps.append('2. Найдем коэффициенты квадратного уравнения:')
        steps.append(f'   a = {a}, b = {b}, c = {c}')
        steps.append(f'   Дискриминант D = b² - 4ac = {b}² - 4·{a}·{c} = {D}')

        # Анализ дискриминанта
        if D > 0:
            steps.append('   D > 0 ⇒ уравнение имеет два действительных корня')

            # Находим корни для y
            y_roots = ex.answer_quadratic_equation(task.replace('x²', 'x').replace('x⁴', 'x²'))
            if isinstance(y_roots, str):
                y_roots = y_roots.split()

            y1, y2 = y_roots[0], y_roots[1]

            steps.append('3. Найдем корни для y:')
            steps.append(f'   y₁ = (-b - √D)/(2a) = {y1}')
            steps.append(f'   y₂ = (-b + √D)/(2a) = {y2}')

            steps.append('4. Сделаем обратную подстановку x² = y:')

            # Анализ корней для y и вычисление конечных корней
            real_roots_numeric = []  # Для численных значений
            real_roots_symbolic = []  # Для символьного представления

            # Обработка y1
            try:
                y1_val = float(y1)
                if y1_val > 0:
                    root1 = y1_val ** 0.5
                    root2 = -y1_val ** 0.5
                    steps.append(f'   x² = {y1} ⇒ x = ±√{y1} ≈ ±{round(root1, 2)}')
                    real_roots_numeric.extend([round(root1, 2), round(root2, 2)])
                    real_roots_symbolic.extend([f'√{y1}', f'-√{y1}'])
                elif y1_val == 0:
                    steps.append(f'   x² = {y1} ⇒ x = 0')
                    real_roots_numeric.append(0.0)
                    real_roots_symbolic.append('0')
                else:
                    steps.append(f'   x² = {y1} < 0 ⇒ действительных корней нет')
            except:
                if y1.startswith('-'):
                    steps.append(f'   x² = {y1} < 0 ⇒ действительных корней нет')
                else:
                    # Пытаемся вычислить численное значение
                    numeric_val = calculate_and_round_roots(y1)
                    if isinstance(numeric_val, (int, float)):
                        root1 = abs(numeric_val) ** 0.5
                        steps.append(f'   x² = {y1} ⇒ x = ±{y1} ≈ ±{round(root1, 2)}')
                        real_roots_numeric.extend([round(root1, 2), round(-root1, 2)])
                    else:
                        steps.append(f'   x² = {y1} ⇒ x = ±{y1}')
                    real_roots_symbolic.extend([y1, f'-{y1}'])

            # Обработка y2
            try:
                y2_val = float(y2)
                if y2_val > 0:
                    root1 = y2_val ** 0.5
                    root2 = -y2_val ** 0.5
                    steps.append(f'   x² = {y2} ⇒ x = ±√{y2} ≈ ±{round(root1, 2)}')
                    real_roots_numeric.extend([round(root1, 2), round(root2, 2)])
                    real_roots_symbolic.extend([f'√{y2}', f'-√{y2}'])
                elif y2_val == 0:
                    steps.append(f'   x² = {y2} ⇒ x = 0')
                    if 0.0 not in real_roots_numeric:
                        real_roots_numeric.append(0.0)
                    if '0' not in real_roots_symbolic:
                        real_roots_symbolic.append('0')
                else:
                    steps.append(f'   x² = {y2} < 0 ⇒ действительных корней нет')
            except:
                if y2.startswith('-'):
                    steps.append(f'   x² = {y2} < 0 ⇒ действительных корней нет')
                else:
                    # Пытаемся вычислить численное значение
                    numeric_val = calculate_and_round_roots(y2)
                    if isinstance(numeric_val, (int, float)):
                        root1 = abs(numeric_val) ** 0.5
                        steps.append(f'   x² = {y2} ⇒ x = ±{y2} ≈ ±{round(root1, 2)}')
                        real_roots_numeric.extend([round(root1, 2), round(-root1, 2)])
                    else:
                        steps.append(f'   x² = {y2} ⇒ x = ±{y2}')
                    real_roots_symbolic.extend([y2, f'-{y2}'])

            # Убираем дубликаты и сортируем численные корни
            real_roots_numeric = sorted(list(set(real_roots_numeric)))

            # Формируем окончательный ответ
            if real_roots_numeric:
                steps.append('5. Действительные корни исходного уравнения:')
                numeric_str = '; '.join([f'{x:.2f}' if x != 0 else '0' for x in real_roots_numeric])
                steps.append(f'   x = {numeric_str}')
                final_answer = ' '.join([f'{x:.2f}' if x != 0 else '0' for x in real_roots_numeric])
            else:
                steps.append('5. Уравнение не имеет действительных корней')
                final_answer = 'корней нет'

        elif D == 0:
            steps.append('   D = 0 ⇒ уравнение имеет один корень (кратности 2)')

            # Находим корень для y
            y_root = ex.answer_quadratic_equation(task.replace('x²', 'x').replace('x⁴', 'x²'))
            if isinstance(y_root, str) and ' ' in y_root:
                y_root = y_root.split()[0]

            steps.append(f'3. Найдем корень для y: y = -b/(2a) = {y_root}')
            steps.append('4. Сделаем обратную подстановку x² = y:')

            # Анализ корня для y и вычисление конечных корней
            real_roots_numeric = []

            try:
                y_val = float(y_root)
                if y_val > 0:
                    root1 = y_val ** 0.5
                    root2 = -y_val ** 0.5
                    steps.append(f'   x² = {y_root} ⇒ x = ±√{y_root} ≈ ±{round(root1, 2)}')
                    real_roots_numeric = [round(root1, 2), round(root2, 2)]
                    real_roots_symbolic = [f'√{y_root}', f'-√{y_root}']
                elif y_val == 0:
                    steps.append(f'   x² = {y_root} ⇒ x = 0')
                    real_roots_numeric = [0.0]
                    real_roots_symbolic = ['0']
                else:
                    steps.append(f'   x² = {y_root} < 0 ⇒ действительных корней нет')
                    real_roots_numeric = []
                    real_roots_symbolic = []
            except:
                if y_root.startswith('-'):
                    steps.append(f'   x² = {y_root} < 0 ⇒ действительных корней нет')
                    real_roots_numeric = []
                    real_roots_symbolic = []
                else:
                    numeric_val = calculate_and_round_roots(y_root)
                    if isinstance(numeric_val, (int, float)):
                        root1 = abs(numeric_val) ** 0.5
                        steps.append(f'   x² = {y_root} ⇒ x = ±{y_root} ≈ ±{round(root1, 2)}')
                        real_roots_numeric = [round(root1, 2), round(-root1, 2)]
                    else:
                        steps.append(f'   x² = {y_root} ⇒ x = ±{y_root}')
                    real_roots_symbolic = [y_root, f'-{y_root}']

            # Сортируем корни
            real_roots_numeric.sort()
            real_roots_symbolic.sort(key=lambda x: x.startswith('-'))

            # Формируем окончательный ответ
            if real_roots_numeric:
                steps.append('5. Действительные корни исходного уравнения:')
                numeric_str = '; '.join([f'{x:.2f}' if x != 0 else '0' for x in real_roots_numeric])
                steps.append(f'   x = {numeric_str}')
                final_answer = ' '.join([f'{x:.2f}' if x != 0 else '0' for x in real_roots_numeric])
            else:
                steps.append('5. Уравнение не имеет действительных корней')
                final_answer = 'корней нет'

        else:  # D < 0
            steps.append('   D < 0 ⇒ квадратное уравнение не имеет действительных корней')
            steps.append('3. Следовательно, исходное биквадратное уравнение также')
            steps.append('   не имеет действительных корней')
            final_answer = 'корней нет'

        steps.append(f'Ответ: {final_answer}')

    except Exception as e:
        steps.append('Ошибка при решении уравнения')
        steps.append(f'Детали: {str(e)}')

    return steps


def get_irrational_solution(task):
    """
    Функция для получения пошагового решения иррационального уравнения √(ax + b) = cx + d
    """
    steps = []

    # Шаг 1: Находим коэффициенты уравнения
    steps.append('1. Находим коэффициенты уравнения:')
    a, b, c, d = ex.find_coofs_irrational_equation(task)
    steps.append(f'   Коэффициенты: a = {a}, b = {b}, c = {c}, d = {d}')

    # Шаг 2: Анализ уравнения и условия существования
    left_part = task.split(' = ')[1]  # получаем выражение из левой части уравнения
    definition = -d / c
    definition = int(definition) if definition.is_integer() else round(definition, 2) if len(
        str(definition)) > 10 else definition
    steps.append('2. Анализ уравнения и условия существования:')
    steps.append('   Уравнение вида √f(x) = g(x)')
    steps.append('   Для существования решения должно выполняться условие:')
    steps.append('   Правая часть неотрицательна: g(x) ≥ 0 (т.к. квадратный корень всегда ≥ 0)')
    steps.append(f'  В нашем случае {left_part} ≥ 0')
    steps.append(f'  Получим неравенство x ≥ {definition}')

    # Шаг 3: Возведение в квадрат
    right_part = task.split(' = ')[0]  # получаем выражение из правой части уравнения
    under_root = right_part.replace('√', '').replace('(', '').replace(')', '')
    steps.append('3. Возведем обе части уравнения в квадрат:')
    steps.append(f'   ({right_part})² = ({left_part})²')
    steps.append(f'   {under_root} = ({left_part})²')
    steps.append(
        '    Неотрицательность подкоренного выражения можно не проверять, так как оно равно квадрату некоторого выражения, а квадрат всегда ≥ 0')

    # Шаг 4: Раскрытие квадрата в правой части
    a_temp, b_temp, c_temp = c ** 2, 2 * c * d, d ** 2
    steps.append('4. Раскроем квадрат в правой части:')
    right_expanded = f'{ex.generate_equation('quadratic', [a_temp, b_temp, c_temp]).replace(' = 0', '')}'
    steps.append(f'   {under_root} = {right_expanded}')

    # Шаг 5: Перенос всех членов в одну сторону
    steps.append('5. Перенесем все члены в левую часть:')
    equation = f'{under_root} - ({right_expanded}) = 0'
    steps.append(f'   {equation}')

    # Упрощаем
    A = -c ** 2
    B = a - 2 * c * d
    C = b - d ** 2

    simplified = f'{ex.generate_equation('quadratic', [A, B, C])}'
    steps.append(f'   Упростим и получим: {simplified}')

    # Шаг 6: Используем существующую функцию для получения корней
    steps.append('6. Решаем полученное уравнение:')
    roots_result = ex.answer_quadratic_equation(simplified)

    # Анализируем результат
    if roots_result == 'Корней нет':
        steps.append('   Уравнение не имеет действительных корней')
        final_answer = 'Корней нет'

    else:
        steps.append(f'   Найдены корни: {roots_result}')

        # Шаг 7: Проверка условия неотрицательности правой части уравнения
        steps.append('7. Проверяем условие неотрицательности правой части уравнения для найденных корней:')
        steps.append(f'   x ≥ {definition}')

        roots_list = list(map(float, roots_result.split()))

        for root in roots_list:
            if root >= definition:
                steps.append(
                    f'   Корень x = {root} ≥ {definition} ⇒ удовлетворяет условию неотрицательности правой части уравнения')
            else:
                steps.append(
                    f'   Корень x = {root} < {definition} ⇒ не удовлетворяет условию неотрицательности правой части уравнения')

        # Шаг 8: Формирование окончательного ответа
        steps.append('8. Окончательный результат:')
        if ex.answer_irrational_equation(task) != 0.0:
            final_answer = ex.answer_irrational_equation(task).rstrip('.0')
        else:
            final_answer = '0'

    steps.append(f'Ответ: {final_answer}')

    return steps


TASK_CONFIG = {'irrational_equation': {'name': 'Иррациональное уравнение',
                                       'generate_func': ex.generate_irrational_equation,
                                       'check_func': ex.check_answer_irrational_equation,
                                       'points': 40,
                                       'get_solution': lambda task: get_irrational_solution(task)},
               'biquadratic_equation': {'name': 'Биквадратное уравнение',
                                        'generate_func': ex.generate_biquadratic_equation,
                                        'check_func': ex.check_answer_biquadratic_equation,
                                        'points': 30,
                                        'get_solution': lambda task: get_biquadratic_solution(task)},
               'quadratic_equation': {'name': 'Квадратное уравнение',
                                      'generate_func': ex.generate_quadratic_equation,
                                      'check_func': ex.check_answer_quadratic_equation,
                                      'points': 20,
                                      'get_solution': lambda task: [
                                          'Сначала найдем дискриминант квадратного уравнения:',
                                          'Если дискриминант больше нуля, то будет 2 корня',
                                          'Если равен нулю, то будет 1 корень',
                                          'Если меньше нуля, то корней нет.',
                                          f'a = {ex.find_coofs_quadratic_equation(task)[0]}',
                                          f'b = {ex.find_coofs_quadratic_equation(task)[1]}',
                                          f'c = {ex.find_coofs_quadratic_equation(task)[2]}',
                                          f'D = b² - 4ac; D = {ex.find_discriminant(task)}',
                                          *(['Теперь можно найти корни уравнения:',
                                             'x₁ = (-b - √D) / 2a',
                                             f'x₁ = {ex.answer_quadratic_equation(task).split()[0]}',
                                             'x₂ = (-b + √D) / 2a',
                                             f'x₂ = {ex.answer_quadratic_equation(task).split()[1]}',
                                             f'Ответ: {ex.answer_quadratic_equation(task)}']
                                            if ex.find_discriminant(task) > 0 else
                                            ['Теперь можно найти корень уравнения:',
                                             'x = -b / 2a', f'x = {ex.answer_quadratic_equation(task)}',
                                             f'Ответ: {ex.answer_quadratic_equation(task)}']
                                            if ex.find_discriminant(task) == 0 else
                                            ['Так как дискриминант меньше нуля, корней нет',
                                             'Ответ: корней нет'])]},
               'linear_equation': {'name': 'Линейное уравнение',
                                   'generate_func': ex.generate_linear_equation,
                                   'check_func': ex.check_answer_linear_equation,
                                   'points': 15,
                                   'get_solution': lambda task:
                                   ['Для того, чтобы решить линейное уравнение нужно все коэффициенты с "х"',
                                    'перенести в одну часть уравнения, а остальные в другую.',
                                    f'{task[:2].strip()} = {ex.get_coofs_linear_equation(task)[2] - ex.get_coofs_linear_equation(task)[1]}',
                                    f'Разделим обе части уравнения на коэффициент перед "х" ({ex.get_coofs_linear_equation(task)[0]}) и получим ответ.',
                                    f'x = {ex.answer_linear_equation(task)}',
                                    f'Ответ: {ex.answer_linear_equation(task)}']}}

OPERATIONS_CONFIG = {'sum': {'sum': 'сложим', 'name': 'Пример на сложение', 'points': [5, 8, 10]},
                     'min': {'min': 'вычтем', 'name': 'Пример на вычитание', 'points': [5, 8, 10]},
                     'mul': {'mul': 'перемножим', 'name': 'Пример на умножение', 'points': [7, 10, 12]},
                     'crop': {'crop': 'разделим', 'name': 'Пример на деление', 'points': [10, 12, 15]}}
