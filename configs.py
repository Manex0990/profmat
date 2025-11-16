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
            real_roots_symbolic = sorted(list(set(real_roots_symbolic)),
                                         key=lambda x: (x.startswith('-'), x))

            # Формируем окончательный ответ
            if real_roots_numeric:
                steps.append('5. Действительные корни исходного уравнения:')
                symbolic_str = '; '.join(real_roots_symbolic)
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
                symbolic_str = '; '.join(real_roots_symbolic)
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


TASK_CONFIG = {'biquadratic_equation': {'name': 'Биквадратное уравнение',
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
