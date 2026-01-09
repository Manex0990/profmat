import functools
from random import randint, uniform, choice
from typing import List, Tuple
import itertools
import re


class MyMath:
    def __init__(self):
        self.equation_types = {
            'linear': {'patterns': [(r'([+-]?\d*)x', 'a'),  # коэффициент при x
                                    (r'(?:(?<=x)|^)([+-]?\d+)(?=[^\d]*=)', 'b'),  # свободный член слева
                                    (r'=\s*([+-]?\d+)', 'c')],
                       'format_terms': ['x', '']},
            'linear_inequation': {'patterns': [],
                                  'format_terms': ['x', '', 'x', '', 'x', '', 'x', '']},
            'quadratic': {'patterns': [(r'([+-]?\d*)x²', 'a'),  # x²
                                       (r'([+-]?\d*)x(?!²)', 'b'),  # x
                                       (r'([+-]?\d+)(?!.*x)', 'c')],
                          'format_terms': ['x²', 'x', '']},
            'biquadratic': {'patterns': [(r'([+-]?\d*)x⁴', 'a'),  # x⁴
                                         (r'([+-]?\d*)x²(?!⁴)', 'b'),  # x²
                                         (r'([+-]?\d+)(?!.*x)', 'c')],
                            'format_terms': ['x⁴', 'x²', '']},
            'irrational': {'patterns': [(r'√\s*\(\s*([+-]?\d*)x', 'a'),  # под корнем перед x
                                        (r'√\s*\(\s*[^)]*?([+-]?\d+)(?:\s*[^x]|$)', 'b'),  # свободный член под корнем
                                        (r'=\s*([+-]?\d*)x', 'c'),  # x вне корня (правая часть уравнения)
                                        (r'=\s*[^=]*?([+-]?\d+)(?:\s*[^x]|$)', 'd')],
                           # свободный член вне корня (правая часть уравнения)
                           'format_terms': ['x', '', 'x', '']},
            'module': {'patterns': [(r'\|[^|]*?([+-]?\d*(?=\s*x))x', 'a'),
                                    # Коэффициент a перед x внутри модуля
                                    (r'\|[^|]*?x\s*([+-]?\s*\d+)|^\|\s*([+-]?\d+)(?![^|]*x)', 'b'),
                                    # Свободный член b внутри модуля
                                    (r'=\s*[^|]*?([+-]?\d*(?=\s*x))x', 'c'),
                                    # Коэффициент c перед x вне модуля (правая часть)
                                    (r'=\s*[^|]*?(?:x\s*([+-]?\s*\d+)|([+-]?\d+)(?!\s*x))', 'd')
                                    # Свободный член d вне модуля
                                    ]}}
        self.OPERATIONS = {'s': sum,
                           'm': lambda nums: nums[0] - sum(nums[1:]),
                           'mul': lambda nums: self.product(nums),
                           'cr': lambda nums: self.divide_sequence(nums)}
        self.symbols_change = {'>': '<',
                               '<': '>',
                               '≤': '≥',
                               '≥': '≤'}

    def generate_random_numbers(self) -> List[int]:
        # два разные множества чисел введены для того, чтобы уравнения чаще имели действительные решения
        nums_range_1 = list(
            itertools.chain(range(-9, 0), range(1, 10)))  # диапазон целых чисел от -9 до 9, не включая 0
        nums_range_2 = list(itertools.chain(range(-5, 0), range(1, 6)))  # диапазон целых чисел от -5 до 5, не включая 0
        a = choice(nums_range_1)
        b = choice(nums_range_1)
        c = choice(nums_range_2)
        d = choice(nums_range_1)
        return [a, b, c, d]

    def generate_random_symbol(self) -> str:
        return choice(['<', '>', '≤', '≥'])

    def format_equation_term(self, coeff: int, variable: str = '', is_first: bool = False) -> str:
        """Форматирует коэффициент уравнения"""
        if not is_first:
            sign = " + " if coeff > 0 else " - "
        else:
            sign = '' if coeff > 0 else '-'

        abs_coeff = abs(coeff)

        if variable:
            if abs_coeff == 1:
                return f"{sign}{variable}"
            else:
                return f"{sign}{abs_coeff}{variable}"
        else:
            return f"{sign}{abs_coeff}"

    def format_inequation_term(self, x_coef, x_term, const, const_term, is_first=False):
        """Форматирование скобок линейного неравенства"""
        if x_coef < 0:
            # Если коэффициент перед x отрицательный, то он меняется местами со свободным членом скобки
            x_part = self.format_equation_term(x_coef, x_term, False)
            const_part = self.format_equation_term(abs(const), const_term, is_first)
            return f'({const_part}{x_part})'
        else:
            # Для положительных коэффициентов перед x
            x_part = self.format_equation_term(x_coef, x_term, is_first)
            const_part = self.format_equation_term(const, const_term)
            return f'({x_part}{const_part})'

    def generate_equation(self, eq_type: str, use_not_random_coofs=None) -> str:
        """Генерирует уравнение заданного типа"""
        if not use_not_random_coofs:
            a, b, c, d = self.generate_random_numbers()
        else:
            a, b, c = use_not_random_coofs  # генерирует уравнение с конкретно заданными коэффициентами
        terms = self.equation_types[eq_type]['format_terms']
        equation = self.format_equation_term(a, terms[0], True)
        equation += self.format_equation_term(b, terms[1])
        equation += self.format_equation_term(c, terms[2]) if len(terms) > 2 else ''
        return f"{equation} = 0"

    def generate_linear_equation(self) -> str:
        """Генерирует линейное уравнение вида ax + b = c, при отрицательном a: b - ax = c"""
        a, b, c = self.generate_random_numbers()[:3]
        terms = self.equation_types['linear']['format_terms']

        if a < 0:
            equation = self.format_inequation_term(abs(b), terms[1], a, terms[0], True)[1:-1]
        else:
            equation = self.format_inequation_term(a, terms[0], b, terms[1], True)[1:-1]
        equation += f' = {c}'
        return equation

    def generate_quadratic_equation(self) -> str:
        """Генерирует квадратное уравнение вида ax² + bx + c = 0"""
        return self.generate_equation('quadratic')

    def generate_biquadratic_equation(self) -> str:
        """Генерирует биквадратное уравнение вида ax⁴ + bx² + c = 0"""
        return self.generate_equation('biquadratic')

    def generate_irrational_equation(self) -> str:
        """Генерирует иррациональное уравнение вида √(ax + b) = cx + d"""
        a, b, c, d = self.generate_random_numbers()
        terms = self.equation_types['irrational']['format_terms']

        left_side = self.format_equation_term(a, terms[0], True)
        left_side += self.format_equation_term(b, terms[1])
        right_side = self.format_equation_term(c, terms[2], True)
        right_side += self.format_equation_term(d, terms[3])

        return f'√({left_side}) = {right_side}'

    def generate_module_equation(self) -> str:
        """Генерирует уравнение с модулем вида |ax + b| = cx + d"""
        return self.generate_irrational_equation().replace('√', '').replace('(', '|').replace(')', '|')

    def generate_linear_inequation(self) -> str:
        """Генерирует линейное неравенство вида (ax + b)(cx + d)(ex + f)(gx + h) ><≥≤ 0"""
        a, b, c, d = self.generate_random_numbers()
        a_x, b_x, c_x, d_x = self.generate_random_numbers()
        terms = self.equation_types['linear_inequation']['format_terms']

        inequation = self.format_inequation_term(a_x, terms[0], a, terms[1], True)
        inequation += self.format_inequation_term(b_x, terms[2], b, terms[3], True)
        inequation += self.format_inequation_term(c_x, terms[4], c, terms[5], True)
        inequation += self.format_inequation_term(d_x, terms[6], d, terms[7], True)

        symbol = self.generate_random_symbol()
        return f'{inequation} {symbol} 0'

    def normalize_linear_equation_format(self, equation: str) -> str:
        """Нормализует линейное уравнение: преобразует b - ax = c в -ax + b = c для парсинга"""
        # Убираем пробелы
        eq = equation.replace(' ', '')

        # Разделяем на левую и правую части
        if '=' not in eq:
            return equation

        left_part, right_part = eq.split('=')

        # Проверяем формат b - ax
        # Паттерн для формата: число, потом минус, потом коэффициент и x
        pattern = r'^([+-]?\d+)-(\d*)x(.*)'
        match = re.match(pattern, left_part)

        if match:
            b_str = match.group(1)
            a_str = match.group(2)
            rest = match.group(3) or ''

            b = int(b_str)
            a = int(a_str) if a_str else 1  # если коэффициент не указан, значит это 1

            # Преобразуем в формат -ax + b
            if a == 1:
                normalized_left = f"-x"
            else:
                normalized_left = f"-{a}x"

            # Добавляем b
            if b != 0:
                if b > 0:
                    normalized_left += f" + {b}"
                else:
                    normalized_left += f" {b}"  # b уже отрицательное

            # Добавляем остаток если есть
            normalized_left += rest

            return f"{normalized_left} = {right_part}"

        return equation

    def find_coefficients(self, equation: str, eq_type: str) -> List[int]:
        """Находит коэффициенты уравнения"""
        # Для линейных уравнений сначала нормализуем формат
        if eq_type == 'linear':
            equation = self.normalize_linear_equation_format(equation)

        # Убираем пробелы
        clean_eq = equation.replace(' ', '')
        coefficients = {'a': 0, 'b': 0, 'c': 0, 'd': 0}

        for pattern, coeff_name in self.equation_types[eq_type]['patterns']:
            match = re.search(pattern, clean_eq)
            if match:
                coeff_str = match.group(1)
                if not coeff_str or coeff_str == '+':
                    coefficients[coeff_name] = 1
                elif coeff_str == '-':
                    coefficients[coeff_name] = -1
                else:
                    coefficients[coeff_name] = int(coeff_str)

        if eq_type == 'linear':
            return [coefficients['a'], coefficients['b'], coefficients['c']]
        elif eq_type in ['quadratic', 'biquadratic']:
            return [coefficients['a'], coefficients['b'], coefficients['c']]
        else:  # irrational
            return [coefficients['a'], coefficients['b'], coefficients['c'], coefficients['d']]

    def find_coofs_linear_equation(self, equation: str) -> List[int]:
        return self.find_coefficients(equation, 'linear')

    def find_coofs_quadratic_equation(self, equation: str) -> List[int]:
        return self.find_coefficients(equation, 'quadratic')

    def find_coofs_biquadratic_equation(self, equation: str) -> List[int]:
        return self.find_coefficients(equation, 'biquadratic')

    def find_coofs_irrational_equation(self, equation: str) -> List[int]:
        return self.find_coefficients(equation, 'irrational')

    def find_coofs_module_equation(self, equation: str) -> List[int]:
        return self.find_coefficients(equation, 'module')

    def calculate_discriminant(self, a: int, b: int, c: int) -> float:
        """Вычисляет дискриминант"""
        return b ** 2 - 4 * a * c

    def find_discriminant(self, quadratic_equation: str) -> float:
        a, b, c = self.find_coofs_quadratic_equation(quadratic_equation)
        return self.calculate_discriminant(a, b, c)

    def find_discriminant_biquadratic(self, biquadratic_equation: str) -> float:
        a, b, c = self.find_coofs_biquadratic_equation(biquadratic_equation)
        return self.calculate_discriminant(a, b, c)

    def process_root(self, root: float) -> float:
        """Обрабатывает и округляет корень"""
        return int(root) if root.is_integer() else round(root, 2) if len(str(root)) > 10 else float(root)

    def solve_quadratic_equation(self, a: int, b: int, c: int) -> List[float]:
        """Решает квадратное уравнение и возвращает корни"""
        d = self.calculate_discriminant(a, b, c)
        if d < 0:
            return []
        elif d == 0:
            return [self.process_root(-b / (2 * a))]
        else:
            roots = [
                (-b - d ** 0.5) / (2 * a),
                (-b + d ** 0.5) / (2 * a)
            ]
            return sorted([self.process_root(r) for r in roots])

    def answer_linear_equation(self, linear_equation: str) -> str:
        """Находит корень линейного уравнения"""
        a, b, c = self.find_coofs_linear_equation(linear_equation)
        x = (c - b) / a
        return str(self.process_root(x))

    def answer_quadratic_equation(self, quadratic_equation: str) -> str:
        """Находит корни квадратного уравнения"""
        a, b, c = self.find_coofs_quadratic_equation(quadratic_equation)
        roots = self.solve_quadratic_equation(a, b, c)
        if not roots:
            return "Корней нет"
        return ' '.join(
            str(int(x)) if x.is_integer() else str(round(x, 2)) if len(str(x)) > 10 else str(x) for x in roots)

    def answer_biquadratic_equation(self, biquadratic_equation: str) -> str:
        """Находит корни биквадратного уравнения"""
        a, b, c = self.find_coofs_biquadratic_equation(biquadratic_equation)
        # Решаем относительно y = x²
        y_roots = self.solve_quadratic_equation(a, b, c)
        if not y_roots:
            return "Корней нет"
        # Извлекаем корни из неотрицательных значений y
        final_roots = []
        for y in y_roots:
            if y > 0:
                sqrt_y = y ** 0.5
                final_roots.extend([-sqrt_y, sqrt_y])
            elif y == 0:
                final_roots.append(0.0)
        if not final_roots:
            return "Корней нет"
        processed_roots = []
        for root in final_roots:
            processed_root = self.process_root(root)
            if processed_root not in processed_roots:
                processed_roots.append(processed_root)
        processed_roots.sort()
        return ' '.join(
            str(int(x)) if x.is_integer() else str(round(x, 2)) if len(str(x)) > 10 else str(x) for x in
            processed_roots)

    def check_routs_on_definition(self, routs: str, definition: float, c: int) -> List[float]:
        ans = []
        for route in list(map(float, routs.split())):
            if (c > 0 and route >= definition) or (c < 0 and route <= definition):
                ans.append(str(route))
        return ans

    def answer_irrational_equation(self, irrational_equation: str) -> str:
        """Находит корни иррационального уравнения"""
        a, b, c, d = self.find_coofs_irrational_equation(irrational_equation)

        # создаем вспомогательное уравнение и находим его корни
        a_new, b_new, c_new = c ** 2, (c * d * 2) - a, (d ** 2) - b
        temp_eq = self.generate_equation('quadratic', [a_new, b_new, c_new])
        routs = self.answer_quadratic_equation(temp_eq)
        if routs == 'Корней нет':
            return 'Корней нет'
        eq_definition = -d / c

        # проверяем корни по области определения
        ans = self.check_routs_on_definition(routs, eq_definition, c)

        return ' '.join(
            str(int(x)) if x.is_integer() else str(round(x, 2)) if len(str(x)) > 10 else str(x) for x in
            list(map(float, ans))) if ans else 'Корней нет'

    def answer_module_equation(self, module_equation: str) -> str:
        """Находит корни уравнения с модулем"""
        a, b, c, d = self.find_coofs_module_equation(module_equation)
        eq_definition = -d / c

        # если коэффициенты при x и коэффициенты без x в обеих частях уравнения совпадают по модулю, решением будет область определения
        if (a == c and b == d) or (a == -c and b == -d):
            eq_definition = int(eq_definition) if eq_definition.is_integer() else round(eq_definition, 2) if len(
                str(eq_definition)) > 10 else eq_definition
            if c > 0:
                return f'[{eq_definition};+∞)'
            else:
                return f'(-∞;{eq_definition}]'

        if (a == c and b > d) or (a == -c and d < -b):
            return 'Корней нет'

        # создаем вспомогательное уравнение и находим его корни
        a_new, b_new, c_new = (c ** 2) - (a ** 2), (c * d * 2) - (a * b * 2), (d ** 2) - (b ** 2)
        temp_eq = self.generate_equation('quadratic', [a_new, b_new, c_new])
        routs = self.answer_quadratic_equation(temp_eq)
        if routs == 'Корней нет':
            return 'Корней нет'

        # проверяем корни по области определения
        ans = self.check_routs_on_definition(routs, eq_definition, c)

        return ' '.join(
            str(int(x)) if x.is_integer() else str(round(x, 2)) if len(str(x)) > 10 else str(x) for x in
            list(map(float, ans))) if ans else 'Корней нет'

    def determine_sign(self, expression_coeffs: List[float], x_value: float, symbol: str) -> bool:
        """Анализ знака неравенства при определенном значении x"""
        symbol = -1 if symbol == '<' or symbol == '≤' else 1
        total_sign = 1
        for a, b in expression_coeffs:
            value = a * x_value + b
            sign = 1 if value > 0 else -1
            total_sign *= sign

        return total_sign == symbol  # 1 - знак совпадает, промежуток идет в ответ, 0 - не совпадает и не идет в ответ

    def get_single_zeros(self, temp_solution: str, zeros: List[str]) -> List:
        """Находит отдельные точки удовлетворяющие неравенству, но не входящие в интервалы промежуточного решения"""
        single_zeros = []
        for zero in zeros:
            if zero not in temp_solution and zero not in single_zeros:
                single_zeros.append(zero)
        return sorted(single_zeros, key=lambda x: float(x))

    def answer_linear_inequation(self, task: str) -> str:
        """Находит решение линейного неравенства"""
        brackets = task.replace(' > 0', '').replace(' < 0', '').replace(' ≤ 0', '').replace(' ≥ 0', '')[1:-1].split(
            ')(')
        symbol = task.split()[-2]

        linear_answers = []  # список значений x - нулей каждой скобки
        intervals = []  # список всех интервалов
        coeffs = []

        for bracket in brackets:
            linear_temp = bracket + ' = 0'
            bracket_coeffs = self.find_coofs_linear_equation(linear_temp)
            coeffs.append(tuple(bracket_coeffs[:-1]))
            answer_temp = self.answer_linear_equation(linear_temp)
            linear_answers.append(answer_temp.rstrip('.0'))
        linear_answers = sorted(linear_answers, key=lambda x: float(x))

        # если знак неравенства нестрогий, то скобки квадратные, иначе круглые
        interval_brackets = ('[', ']') if '≥' in task or '≤' in task else ('(', ')')

        # форматируем строковые представления интервалов
        if self.determine_sign(coeffs, float(linear_answers[0]) - 1, symbol):
            intervals.append(f'(-∞;{linear_answers[0]}{interval_brackets[1]}')  # (-∞;a)
        for i in range(3):
            if self.determine_sign(coeffs, (float(linear_answers[i]) + float(linear_answers[i + 1])) / 2, symbol) and \
                    linear_answers[i] != linear_answers[i + 1]:  # промежутки по типу (2;2) не берем
                intervals.append(
                    f'{interval_brackets[0]}{linear_answers[i]};{linear_answers[i + 1]}{interval_brackets[1]}')  # (a;b)
        if self.determine_sign(coeffs, float(linear_answers[-1]) + 1, symbol):
            intervals.append(f'{interval_brackets[0]}{linear_answers[-1]};+∞)')  # (а;+∞)

        result = ' ∪ '.join(intervals)
        result_copy = result

        # совмещаем интервалы вида (-∞;-2] ∪ [-2;-1.8] в (-∞;-1.8]
        pattern = r'-?\d+(?:\.\d+)?\] ∪ \[-?\d+(?:\.\d+)?;'
        matches = re.findall(pattern, result)
        if matches:
            for match in matches:
                temp = match.replace(';', '').split('] ∪ [')
                if temp[0] == temp[1]:
                    result = result.replace(match, '')

        # Проверяем отдельные точки (корни)
        if symbol == '≥' or symbol == '≤':
            single_zeros = self.get_single_zeros(result_copy, linear_answers)
            if single_zeros:
                if result == '':
                    return f'{{{'; '.join(single_zeros)}}}'
                else:
                    result += f' ∪ {{{'; '.join(single_zeros)}}}'

        # Возвращаем ответ
        if not len(result):
            return 'Корней нет'
        return result

    def check_answer(self, task: str, user_answer: str, eq_type: str) -> List:
        """Проверяет ответ для уравнения"""
        match eq_type:
            case 'linear':
                correct_answer = self.answer_linear_equation(task).rstrip('.0')
            case 'quadratic':
                correct_answer = self.answer_quadratic_equation(task).rstrip('.0')
            case 'biquadratic':
                correct_answer = self.answer_biquadratic_equation(task).rstrip('.0')
            case 'irrational':
                correct_answer = self.answer_irrational_equation(task).rstrip('.0')
            case 'module':
                correct_answer = self.answer_module_equation(task).rstrip('.0')
            case 'linear_inequation':
                correct_answer = self.answer_linear_inequation(task).rstrip('.0')

        user_ans = str(user_answer).strip().rstrip('.0')
        is_correct = str(user_ans) == correct_answer
        message = ("Верно. Продолжайте в том же духе." if is_correct
                   else "Неверно. Проверьте расчёты и попробуйте еще раз.")
        return [message, is_correct, eq_type]

    def check_answer_linear_equation(self, task: str, user_answer: str) -> List:
        return self.check_answer(task, user_answer, 'linear')

    def check_answer_quadratic_equation(self, task: str, user_answer: str) -> List:
        return self.check_answer(task, user_answer, 'quadratic')

    def check_answer_biquadratic_equation(self, task: str, user_answer: str) -> List:
        return self.check_answer(task, user_answer, 'biquadratic')

    def check_answer_irrational_equation(self, task: str, user_answer: str) -> List:
        return self.check_answer(task, user_answer, 'irrational')

    def check_answer_module_equation(self, task: str, user_answer: str) -> List:
        return self.check_answer(task, user_answer, 'module')

    def check_answer_linear_inequation(self, task: str, user_answer: str) -> List:
        return self.check_answer(task, user_answer, 'linear_inequation')

    def parse_numbers(self, task: str) -> List[float]:
        """Парсит числа из строки задачи"""
        numbers = re.findall(r'-?\d+\.?\d*', task)
        return [float(num) for num in numbers]

    def identify_task_type(self, task: str) -> Tuple[str, int]:
        """Определяет тип задачи и уровень сложности"""
        numbers = self.parse_numbers(task)

        if len(numbers) == 2:
            stage = 1 if all(num == int(num) for num in numbers) else 2
        elif len(numbers) == 4:
            stage = 3
        else:
            stage = 1

        operator_map = {'+': 's', '-': 'm', '*': 'mul', ':': 'cr'}
        for op, code in operator_map.items():
            if op in task:
                return code, stage

        return 's', 1

    def answer_for_all_stages(self, task: str) -> str:
        """Находит решение для любого примера"""
        task_type, stage = self.identify_task_type(task)
        numbers = self.parse_numbers(task)

        result = self.OPERATIONS[task_type](numbers)

        # Форматирование результата
        if stage == 1 and task_type in ['s', 'm', 'mul']:
            result = int(round(result, 2))
        else:
            if result.is_integer():
                result = int(result)
            elif len(str(result)) > 10:
                result = round(result, 2)

        return str(result)

    def product(self, numbers: List[float]) -> float:
        """Вычисляет произведение чисел"""
        result = functools.reduce(lambda x, y: x * y, numbers)
        return result

    def divide_sequence(self, numbers: List[float]) -> float:
        """Вычисляет последовательное деление"""
        result = functools.reduce(lambda x, y: x / y, numbers)
        return result

    def check_answer_for_all_stages(self, task: str, user_answer: str) -> List:
        """Проверяет ответ для любого примера"""
        correct_answer = self.answer_for_all_stages(task)

        # Нормализация ответов
        user_ans = str(user_answer).strip().rstrip('.0')
        correct_ans = correct_answer.rstrip('.0')

        is_correct = user_ans == correct_ans
        task_type, stage = self.identify_task_type(task)

        message = "Верно. Продолжайте в том же духе." if is_correct else "Неверно. Проверьте расчеты и попробуйте позже."
        return [message, is_correct, f"{task_type}_{stage}"]

    # Генераторы примеров
    def generate_simple_operation(self, op: str, range1: Tuple, range2: Tuple, integers: bool = True) -> str:
        """Генерирует простой пример с двумя числами"""
        if integers:
            a = randint(*range1)
            b = randint(*range2)
        else:
            a = round(uniform(*range1), 2)
            b = round(uniform(*range2), 2)
        return f"{a} {op} {b} = ?"

    def generate_complex_operation(self, op: str, ranges: List[Tuple], integers: List[bool]) -> str:
        """Генерирует сложный пример с четырьмя числами"""
        numbers = []
        for i, (range_start, range_end) in enumerate(ranges):
            if integers[i]:
                num = randint(range_start, range_end)
            else:
                num = round(uniform(range_start, range_end), 2)
            numbers.append(str(num))

        return f" {op} ".join(numbers) + " = ?"

    # Генераторы для сложения
    def generate_sum_stage_1(self) -> str:
        return self.generate_simple_operation('+', (1, 101), (1, 101))

    def generate_sum_stage_2(self) -> str:
        return self.generate_simple_operation('+', (1, 20), (1, 20), False)

    def generate_sum_stage_3(self) -> str:
        return self.generate_complex_operation('+', [(1, 30), (1, 30), (1, 30), (1, 30)], [True, False, False, True])

    # Генераторы для вычитания
    def generate_min_stage_1(self) -> str:
        return self.generate_simple_operation('-', (1, 101), (1, 101))

    def generate_min_stage_2(self) -> str:
        return self.generate_simple_operation('-', (1, 20), (1, 20), False)

    def generate_min_stage_3(self) -> str:
        return self.generate_complex_operation('-', [(50, 100), (30, 50), (20, 30), (1, 20)],
                                               [True, False, False, True])

    # Генераторы для умножения
    def generate_mul_stage_1(self) -> str:
        return self.generate_simple_operation('*', (1, 21), (1, 21))

    def generate_mul_stage_2(self) -> str:
        return self.generate_simple_operation('*', (1, 10), (1, 10), False)

    def generate_mul_stage_3(self) -> str:
        return self.generate_complex_operation('*', [(1, 10), (1, 10), (1, 10), (1, 10)], [True, False, False, True])

    # Генераторы для деления
    def generate_crop_stage_1(self) -> str:
        return self.generate_simple_operation(':', (1, 51), (1, 51))

    def generate_crop_stage_2(self) -> str:
        return self.generate_simple_operation(':', (1, 20), (1, 20), False)

    def generate_crop_stage_3(self) -> str:
        return self.generate_complex_operation(':', [(10, 40), (1, 8), (1, 6), (1, 4)], [True, False, False, True])


ex = MyMath()
task = '|-3x - 1| = 3x - 1'
print(task)
print(ex.find_coofs_module_equation(task))
print(ex.answer_module_equation(task))
print(ex.check_answer_module_equation(task, ex.answer_module_equation(task)))
