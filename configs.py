from maths import MyMath

ex = MyMath()
secret_key = 'profmat_pet_project_2026_key'


# Функция для вычисления и округления корней
def calculate_and_round_roots(root_str):
    """Вычисляет числовое значение корня и округляет до сотых"""
    try:
        if '√' in root_str:
            number_str = root_str.replace('√', '').replace('-', '')
            number = float(number_str)
            result = number ** 0.5
            if root_str.startswith('-'):
                result = -result
            return round(result, 2)
        else:
            return round(float(root_str), 2)
    except:
        return root_str


def determine_symbol_on_interval(coeffs, root):
    total_sign = 1
    for a, b in coeffs:
        value = a * root + b
        sign = 1 if value > 0 else -1
        total_sign *= sign
    return '+' if total_sign == 1 else '-'


def get_linear_inequality_solution(task):
    """
    Функция для получения пошагового решения линейного неравенства методом интервалов
    """
    steps = []

    steps.append('1. Анализ вида неравенства:')
    inequality_symbol = task.split()[-2]
    expression = task.replace(' > 0', '').replace(' < 0', '').replace(' ≥ 0', '').replace(' ≤ 0', '')
    brackets = expression[1:-1].split(')(')

    if ' ≥ ' in task or ' ≤ ' in task:
        steps.append(f'   Неравенство нестрогое (знак {inequality_symbol})')
    else:
        steps.append(f'   Неравенство строгое (знак {inequality_symbol})')

    steps.append(f'   Исходное выражение: {expression}')

    sign_change_map = {'>': '<', '<': '>', '≥': '≤', '≤': '≥'}

    steps.append("\n2. Преобразуем скобки:")
    steps.append(
        'Нужно привести все скобки к виду, где x со своим коэффициентом будет стоять вначале, а свободный коэффициент - в конце.')
    steps.append(
        'Для этого во всех скобках, где x стоит на последнем месте и коэффициент перед ним отрицательный,')
    steps.append(
        'вынесем минус за скобки и поменяем знаки в скобках, а также поменяем местами свободный коэффициент и x')
    temp = task
    new_expression = expression
    new_symbol = inequality_symbol

    for i, bracket in enumerate(brackets, 1):
        # Проверяем скобки вида (a - bx)
        if ' - ' in bracket and 'x' in bracket.split(' - ')[1]:
            a_part, bx_part = bracket.split(' - ')
            a = a_part[1:] if a_part.startswith('(') else a_part
            bx = bx_part[:-1] if bx_part.endswith(')') else bx_part

            b = bx.replace('x', '').strip()
            b = '1' if b == '' else b
            transformed = f'({b}x - {a})'
            current_symbol = temp.split()[-2]  # текущий знак неравенства
            new_symbol = sign_change_map[current_symbol]  # противоположный знак, при умножении на -1
            expression = temp.replace(' > 0', '').replace(' < 0', '').replace(' ≥ 0', '').replace(' ≤ 0',
                                                                                                  '')  # произведение скобок
            steps.append(f"{i}) {bracket} → выносим минус: = -{transformed}")
            steps.append('Домножим обе части неравенства на -1, чтоб избавиться от минуса за скобками.')
            steps.append('Знак неравенства изменится на противоположный.')
            new_expression = expression.replace(bracket, transformed[1:-1])  # заменяем скобку
            temp = new_expression + f' {new_symbol} ' + '0'  # преобразованное неравенство с новым знаком и скобкой
            steps.append(f"Получим: {temp}")
        else:
            steps.append(f"{i}) {bracket} — стандартный вид, ничего не меняем")

    steps.append(f'Итоговое неравенство: {temp}')

    steps.append('\n3. Находим нули каждого множителя:')

    new_brackets = new_expression[1:-1].split(')(')

    roots = set()
    for i, bracket in enumerate(new_brackets):
        linear_eq = bracket + ' = 0'
        root_str = ex.answer_linear_equation(linear_eq)
        steps.append(f'   {bracket} = 0 → {root_str}')
        roots.add(root_str)
    roots = sorted(list(roots), key=lambda x: float(x))
    steps.append(f'   В порядке возрастания: {', '.join(roots)}')

    steps.append('\n4. Применяем метод интервалов:')
    steps.append('   - Расставляем нули на числовой прямой')
    steps.append('   - Определяем знак выражения на каждом интервале')
    coeffs = []
    for bracket in new_brackets:
        coeffs.append(tuple(ex.find_coofs_linear_equation(bracket + ' = 0'))[:-1])
    symbols_list = []
    for i in range(len(roots) + 1):
        if i == 0:
            symbols_list.append(determine_symbol_on_interval(coeffs, float(roots[i]) - 1))
        elif i == len(roots):
            symbols_list.append(determine_symbol_on_interval(coeffs, float(roots[i - 1]) + 1))
        else:
            symbols_list.append(determine_symbol_on_interval(coeffs, (float(roots[i - 1]) + float(roots[i])) / 2))
    symbols = ' ' * 20
    nums_line = ' ' * 10
    nums = ''
    for symbol in symbols_list:
        symbols += f'{symbol}{' ' * 15}'
    steps.append(symbols)
    for root in roots:
        nums_line += f'{'-' * 10}{'0' if new_symbol in ('<', '>') else '*'}'
        if '0' in nums_line:
            nums += f'{' ' * (10 - len(root) // 2)}{root}'
        else:
            nums += f'{' ' * (14 - len(root) // 2)}{root}'
    nums_line += ('-' * 10 + '>' + 'x')
    steps.append(nums_line)
    steps.append(nums)

    steps.append('   - Выбираем интервалы, удовлетворяющие неравенству')

    steps.append('\n5. Получаем решение:')
    final_answer = ex.answer_linear_inequation(task)
    steps.append(f'   {final_answer}')

    steps.append(f'\nОтвет: {final_answer}')
    return steps


def get_biquadratic_solution(task):
    """
    Функция для получения пошагового решения биквадратного уравнения
    """
    steps = []

    steps.append('1. Сделаем замену переменной: y = x²')
    equation_y = task.replace('x⁴', 'y²').replace('x²', 'y')
    steps.append(f'   Получим: {equation_y}')

    try:
        a, b, c = ex.find_coofs_quadratic_equation(task.replace('x²', 'x').replace('x⁴', 'x²'))
        D = ex.find_discriminant_biquadratic(task)

        steps.append('2. Найдем коэффициенты квадратного уравнения:')
        steps.append(f'   a = {a}, b = {b}, c = {c}')
        steps.append(f'   Дискриминант D = b² - 4ac = {b}² - 4·{a}·{c} = {D}')

        if D > 0:
            steps.append('   D > 0 ⇒ уравнение имеет два действительных корня')

            y_roots = ex.answer_quadratic_equation(task.replace('x²', 'x').replace('x⁴', 'x²'))
            if isinstance(y_roots, str):
                y_roots = y_roots.split()

            y1, y2 = y_roots[0], y_roots[1]

            steps.append('3. Найдем корни для y:')
            steps.append(f'   y₁ = (-b - √D)/(2a) = {y1}')
            steps.append(f'   y₂ = (-b + √D)/(2a) = {y2}')

            steps.append('4. Сделаем обратную подстановку x² = y:')

            real_roots_numeric = []  # Для численных значений
            real_roots_symbolic = []  # Для символьного представления

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
                    numeric_val = calculate_and_round_roots(y2)
                    if isinstance(numeric_val, (int, float)):
                        root1 = abs(numeric_val) ** 0.5
                        steps.append(f'   x² = {y2} ⇒ x = ±{y2} ≈ ±{round(root1, 2)}')
                        real_roots_numeric.extend([round(root1, 2), round(-root1, 2)])
                    else:
                        steps.append(f'   x² = {y2} ⇒ x = ±{y2}')
                    real_roots_symbolic.extend([y2, f'-{y2}'])

            real_roots_numeric = sorted(list(set(real_roots_numeric)))

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

            y_root = ex.answer_quadratic_equation(task.replace('x²', 'x').replace('x⁴', 'x²'))
            if isinstance(y_root, str) and ' ' in y_root:
                y_root = y_root.split()[0]

            steps.append(f'3. Найдем корень для y: y = -b/(2a) = {y_root}')
            steps.append('4. Сделаем обратную подстановку x² = y:')

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

            real_roots_numeric.sort()
            real_roots_symbolic.sort(key=lambda x: x.startswith('-'))

            if real_roots_numeric:
                steps.append('5. Действительные корни исходного уравнения:')
                numeric_str = '; '.join([f'{x:.2f}' if x != 0 else '0' for x in real_roots_numeric])
                steps.append(f'   x = {numeric_str}')
                final_answer = ' '.join([f'{x:.2f}' if x != 0 else '0' for x in real_roots_numeric])
            else:
                steps.append('5. Уравнение не имеет действительных корней')
                final_answer = 'корней нет'

        else:
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

    steps.append('1. Находим коэффициенты уравнения:')
    a, b, c, d = ex.find_coofs_irrational_equation(task)
    steps.append(f'   Коэффициенты: a = {a}, b = {b}, c = {c}, d = {d}')

    left_part = task.split(' = ')[1]  # получаем выражение из левой части уравнения
    definition = -d / c
    definition = int(definition) if definition.is_integer() else round(definition, 2) if len(
        str(definition)) > 10 else definition
    steps.append('2. Анализ уравнения и условия существования:')
    steps.append('   Уравнение вида √f(x) = g(x)')
    steps.append('   Для существования решения должно выполняться условие:')
    steps.append('   Правая часть неотрицательна: g(x) ≥ 0 (т.к. квадратный корень всегда ≥ 0)')
    steps.append(f'  В нашем случае {left_part} ≥ 0')
    if c > 0:
        steps.append(f'  Получим неравенство x ≥ {definition}')
    else:
        steps.append(f'  Получим неравенство x ≤ {definition}')

    right_part = task.split(' = ')[0]  # получаем выражение из правой части уравнения
    under_root = right_part.replace('√', '').replace('(', '').replace(')', '')
    steps.append('3. Возведем обе части уравнения в квадрат:')
    steps.append(f'   ({right_part})² = ({left_part})²')
    steps.append(f'   {under_root} = ({left_part})²')
    steps.append('    Неотрицательность подкоренного выражения можно не проверять,')
    steps.append('    так как оно равно квадрату некоторого выражения, а квадрат всегда ≥ 0')

    a_temp, b_temp, c_temp = c ** 2, 2 * c * d, d ** 2
    steps.append('4. Раскроем квадрат в правой части:')
    right_expanded = f'{ex.generate_equation('quadratic', [a_temp, b_temp, c_temp]).replace(' = 0', '')}'
    steps.append(f'   {under_root} = {right_expanded}')

    steps.append('5. Перенесем все члены в левую часть:')
    equation = f'{under_root} - ({right_expanded}) = 0'
    steps.append(f'   {equation}')

    A = -c ** 2
    B = a - 2 * c * d
    C = b - d ** 2

    simplified = f'{ex.generate_equation('quadratic', [A, B, C])}'
    steps.append(f'   Упростим и получим: {simplified}')

    steps.append('6. Решаем полученное уравнение:')
    roots_result = ex.answer_quadratic_equation(simplified)

    if roots_result == 'Корней нет':
        steps.append('   Уравнение не имеет действительных корней')
        final_answer = 'Корней нет'

    else:
        steps.append(f'   Найдены корни: {roots_result}')

        steps.append('7. Проверяем условие неотрицательности правой части уравнения для найденных корней:')
        if c > 0:
            steps.append(f'   x ≥ {definition}')
        else:
            steps.append(f'   x ≤ {definition}')

        roots_list = list(map(float, roots_result.split()))

        for root in roots_list:
            if c > 0:
                if root >= definition:
                    steps.append(
                        f'   Корень x = {root} ≥ {definition} ⇒ удовлетворяет условию неотрицательности правой части уравнения')
                else:
                    steps.append(
                        f'   Корень x = {root} < {definition} ⇒ не удовлетворяет условию неотрицательности правой части уравнения')
            elif c < 0:
                if root <= definition:
                    steps.append(
                        f'   Корень x = {root} ≤ {definition} ⇒ удовлетворяет условию неотрицательности правой части уравнения')
                else:
                    steps.append(
                        f'   Корень x = {root} > {definition} ⇒ не удовлетворяет условию неотрицательности правой части уравнения')
        steps.append('8. Окончательный результат:')
        if ex.answer_irrational_equation(task) != '0':
            final_answer = ex.answer_irrational_equation(task).rstrip('.0')
        else:
            final_answer = '0'

    steps.append(f'Ответ: {final_answer}')

    return steps


def get_module_solution(task):
    """
    Упрощенная версия решения уравнения с модулем
    """

    steps = []

    a, b, c, d = ex.find_coofs_module_equation(task)
    definition = -d / c
    definition = int(definition) if definition.is_integer() else round(definition, 2) if len(
        str(definition)) > 10 else definition

    if (a == c and b == d) or (a == -c and b == -d):
        steps.append(
            '1. Заметим, что выражение под модулем и в правой части уравнения совпадают или отличаются только знаком')
        steps.append('Значит решением будет являться область определения')
        if c > 0:
            steps.append(f'2. Ответ: [{definition};+∞)')
        else:
            steps.append(f'2. Ответ: (-∞;{definition}]')
        return steps

    if (a == c and b > d) or (a == -c and d < -b):
        steps.append('1. Заметим, что коэффициенты при x совпадают, значит нужно сравнить свободные члены')
        return '2. Ответ: Корней нет'

    left_part, right_part = task.split(' = ')
    steps.append('1. Мы можем возвести обе части уравнения в квадрат при условии, что они не отрицательны.')
    steps.append('2. Левая часть неотрицательна всегда, т.к. модуль не может быть отрицательным.')
    steps.append(f'Для правой части запишем условие: {right_part} ≥ 0')
    if c > 0:
        steps.append(f'  3. Получим неравенство x ≥ {definition}')
    else:
        steps.append(f'  3. Получим неравенство x ≤ {definition}')
    steps.append(f"\n4. Возводим в квадрат: ({left_part})² = ({right_part})²")

    left = ex.generate_equation('quadratic', [a ** 2, 2 * a * b, b ** 2]).replace(' = 0', '')
    right = ex.generate_equation('quadratic', [c ** 2, 2 * c * d, d ** 2]).replace(' = 0', '')
    steps.append(f"Получаем {left} = {right}")

    A = a * a - c * c
    B = 2 * a * b - 2 * c * d
    C = b * b - d * d

    steps.append(f"\n5. Переносим всё влево:")
    new = ex.generate_equation('quadratic', [A, B, C])
    steps.append(new)
    steps.append(f'D = {ex.find_discriminant(new)}')

    solutions = ex.answer_quadratic_equation(new)
    steps.append(f'6. Получаем корни: {solutions}')

    steps.append("\n7. Проверяем корни по ограничению:")
    valid_solutions = ex.check_routs_on_definition(solutions, definition, c)

    for root in list(map(float, solutions.split())):
        if c > 0:
            if root >= definition:
                steps.append(
                    f'   Корень x = {root} ≥ {definition} ⇒ удовлетворяет условию неотрицательности правой части уравнения')
            else:
                steps.append(
                    f'   Корень x = {root} < {definition} ⇒ не удовлетворяет условию неотрицательности правой части уравнения')
        elif c < 0:
            if root <= definition:
                steps.append(
                    f'   Корень x = {root} ≤ {definition} ⇒ удовлетворяет условию неотрицательности правой части уравнения')
            else:
                steps.append(
                    f'   Корень x = {root} > {definition} ⇒ не удовлетворяет условию неотрицательности правой части уравнения')

    steps.append("\n8. Итоговый ответ:")
    if not len(valid_solutions):
        steps.append("Уравнение не имеет решений")
        answer = "Корней нет"
    else:
        answer = ' '.join(map(str, valid_solutions))

    steps.append(f"\nОтвет: {answer.rstrip('.0')}")

    return steps


TASK_CONFIG = {'linear_inequation': {'name': 'Линейное неравенство. Метод интервалов',
                                     'generate_func': ex.generate_linear_inequation,
                                     'check_func': ex.check_answer_linear_inequation,
                                     'points': 50,
                                     'get_solution': lambda task: get_linear_inequality_solution(task)},
               'module_equation': {'name': 'Уравнение с модулем',
                                   'generate_func': ex.generate_module_equation,
                                   'check_func': ex.check_answer_module_equation,
                                   'points': 40,
                                   'get_solution': lambda task: get_module_solution(task)},
               'irrational_equation': {'name': 'Иррациональное уравнение',
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
                                   'points': 10,
                                   'get_solution': lambda task:
                                   ['Для того, чтобы решить линейное уравнение нужно все коэффициенты с "х"',
                                    'перенести в одну часть уравнения, а остальные в другую.',
                                    f'{task[:2].strip()} = {ex.find_coofs_linear_equation(task)[2] - ex.find_coofs_linear_equation(task)[1]}',
                                    f'Разделим обе части уравнения на коэффициент перед "х" ({ex.find_coofs_linear_equation(task)[0]}) и получим ответ.',
                                    f'x = {ex.answer_linear_equation(task)}',
                                    f'Ответ: {ex.answer_linear_equation(task)}']}}

OPERATIONS_CONFIG = {'sum': {'sum': 'сложим', 'name': 'Пример на сложение', 'points': [5, 8, 10]},
                     'min': {'min': 'вычтем', 'name': 'Пример на вычитание', 'points': [5, 8, 10]},
                     'mul': {'mul': 'перемножим', 'name': 'Пример на умножение', 'points': [7, 10, 12]},
                     'crop': {'crop': 'разделим', 'name': 'Пример на деление', 'points': [10, 12, 15]}}

route_mapping = {'linear_equation': 'open_task_linear_equation',
                 'quadratic_equation': 'open_task_quadratic_equation',
                 'biquadratic_equation': 'open_task_biquadratic_equation',
                 'irrational_equation': 'open_task_irrational_equation',
                 'module_equation': 'open_task_module_equation',
                 'linear_inequation': 'open_task_linear_inequation'}

task_type_names = {
    'linear_equation': 'Линейное уравнение',
    'quadratic_equation': 'Квадратное уравнение',
    'biquadratic_equation': 'Биквадратное уравнение',
    'irrational_equation': 'Иррациональное уравнение',
    'module_equation': 'Уравнение с модулем',
    'linear_inequation': 'Линейное неравенство',
    'sum_1': 'Сложение (простой)',
    'sum_2': 'Сложение (средний)',
    'sum_3': 'Сложение (сложный)',
    'min_1': 'Вычитание (простой)',
    'min_2': 'Вычитание (средний)',
    'min_3': 'Вычитание (сложный)',
    'mul_1': 'Умножение (простой)',
    'mul_2': 'Умножение (средний)',
    'mul_3': 'Умножение (сложный)',
    'crop_1': 'Деление (простой)',
    'crop_2': 'Деление (средний)',
    'crop_3': 'Деление (сложный)'
}
