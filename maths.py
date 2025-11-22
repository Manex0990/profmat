import functools
from random import randint, uniform, choice
from typing import List, Tuple
import itertools
import re


class MyMath:
    def __init__(self):
        self.equation_types = {
            'quadratic': {'patterns': [(r'([+-]?\d*)x²', 'a'),  # x²
                                       (r'([+-]?\d*)x(?!²)', 'b'),  # x
                                       (r'([+-]?\d+)(?!.*x)', 'c')],
                          'format_terms': ['x²', 'x', '']},
            'biquadratic': {'patterns': [(r'([+-]?\d*)x⁴', 'a'),  # x⁴
                                         (r'([+-]?\d*)x²(?!⁴)', 'b'),  # x²
                                         (r'([+-]?\d+)(?!.*x)', 'c')], 'format_terms': ['x⁴', 'x²', '']},
            'irrational': {'patterns': [(r'√\W([+-]?\d*)x', 'a'),  # x под корнем
                                        (r'([+-]?\d+)[^x]\W', 'b'),  # свободный член под корнем
                                        (r'[^√]\W([+-]?\d*)x', 'c'),  # x
                                        (r'([+-]?\d*)(?!.*x)', 'd')], 'format_terms': ['x', '', 'x', '']}, }  # свободный член
        self.OPERATIONS = {'s': sum,
                           'm': lambda nums: nums[0] - sum(nums[1:]),
                           'mul': lambda nums: self.product(nums),
                           'cr': lambda nums: self.divide_sequence(nums)}

    def generate_random_numbers(self):
        a = randint(1, 9)
        b = choice(list(itertools.chain(range(-9, 0), range(1, 10))))  # случайное целое число от -9 до 9, не включая 0
        c = choice(list(itertools.chain(range(-9, 0), range(1, 10))))  # случайное целое число от -9 до 9, не включая 0
        d = choice(list(itertools.chain(range(-9, 0), range(1, 10))))  # случайное целое число от -9 до 9, не включая 0
        return a, b, c, d

    def format_equation_term(self, coeff: int, variable: str = '', is_first: bool = False) -> str:
        """Форматирует коэффициент уравнения"""
        sign = ""
        if not is_first:
            sign = " + " if coeff > 0 else " - "

        abs_coeff = abs(coeff)

        if variable:
            if abs_coeff == 1:
                return f"{sign}{variable}" if not is_first else variable
            else:
                return f"{sign}{abs_coeff}{variable}" if not is_first else f"{abs_coeff}{variable}"
        else:
            return f"{sign}{abs_coeff}" if not is_first else str(abs_coeff)

    def generate_equation(self, eq_type: str) -> str:
        """Генерирует уравнение заданного типа"""
        a, b, c, d = self.generate_random_numbers()
        terms = self.equation_types[eq_type]['format_terms']
        equation = self.format_equation_term(a, terms[0], True)
        equation += self.format_equation_term(b, terms[1])
        equation += self.format_equation_term(c, terms[2])
        return f"{equation} = 0"

    def generate_quadratic_equation(self) -> str:
        return self.generate_equation('quadratic')

    def generate_biquadratic_equation(self) -> str:
        return self.generate_equation('biquadratic')

    def generate_irrational_equation(self) -> str:
        a, b, c, d = self.generate_random_numbers()
        terms = self.equation_types['irrational']['format_terms']
        left_side = self.format_equation_term(a, terms[0], True)
        left_side += self.format_equation_term(b, terms[1])
        right_side = self.format_equation_term(c, terms[2], True)
        right_side += self.format_equation_term(d, terms[3])
        return f'√({left_side}) = {right_side}'

    def find_coefficients(self, equation: str, eq_type: str) -> List[int]:
        """Находит коэффициенты уравнения"""
        # Убираем пробелы и "= 0"
        clean_eq = equation.replace(' ', '').replace('=0', '')
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
        return [coefficients['a'], coefficients['b'], coefficients['c']] if eq_type != 'irrational' else [
            coefficients['a'], coefficients['b'], coefficients['c'], coefficients['d']]

    def find_coofs_quadratic_equation(self, equation: str) -> List[int]:
        return self.find_coefficients(equation, 'quadratic')

    def find_coofs_biquadratic_equation(self, equation: str) -> List[int]:
        return self.find_coefficients(equation, 'biquadratic')

    def find_coofs_irrational_equation(self, equation: str) -> List[int]:
        return self.find_coefficients(equation, 'irrational')

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
        return int(root) if root.is_integer() else round(root, 2)

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

    def answer_quadratic_equation(self, quadratic_equation: str) -> str:
        """Находит корни квадратного уравнения"""
        a, b, c = self.find_coofs_quadratic_equation(quadratic_equation)
        roots = self.solve_quadratic_equation(a, b, c)
        return "Корней нет" if not roots else ' '.join(str(x) for x in roots)

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
        return ' '.join(str(x) for x in processed_roots)

    def check_answer(self, task: str, user_answer: str, eq_type: str) -> List:
        """Проверяет ответ для уравнения"""
        if eq_type == 'quadratic':
            correct_answer = self.answer_quadratic_equation(task)
        else:
            correct_answer = self.answer_biquadratic_equation(task)
        is_correct = str(user_answer).strip() == correct_answer
        message = ("Верно. Продолжайте в том же духе." if is_correct
                   else "Неверно. Проверьте расчёты и попробуйте еще раз.")
        return [message, is_correct, eq_type]

    def check_answer_quadratic_equation(self, task: str, user_answer: str) -> List:
        return self.check_answer(task, user_answer, 'quadratic')

    def check_answer_biquadratic_equation(self, task: str, user_answer: str) -> List:
        return self.check_answer(task, user_answer, 'biquadratic')

    def generate_linear_equation(self) -> str:
        """Генерирует линейное уравнение"""
        a, b, c, d = self.generate_random_numbers()

        left_side = self.format_equation_term(a, 'x', True)
        left_side += self.format_equation_term(b)

        return f"{left_side} = {c}"

    def get_coofs_linear_equation(self, task: str) -> List[int]:
        """Находит коэффициенты линейного уравнения"""
        equation = task.replace(" ", "")

        pattern = r'([+-]?\d*)x?([+-]\d+)?=([+-]?\d+)'

        match = re.search(pattern, equation)

        a_str, b_str, c_str = match.groups()

        # Обработка коэффициента a
        if a_str == "" or a_str == "+":
            a = 1
        elif a_str == "-":
            a = -1
        else:
            a = int(a_str)

        # Обработка коэффициента b
        if b_str is None:
            b = 0
        else:
            b = int(b_str)

        # Обработка коэффициента c
        c = int(c_str)

        return [a, b, c]

    def answer_linear_equation(self, linear_equation: str) -> str:
        """Находит корень линейного уравнения"""
        a, b, c = self.get_coofs_linear_equation(linear_equation)
        x = (c - b) / a
        return str(int(x) if x.is_integer() else round(x, 2))

    def check_answer_linear_equation(self, task: str, user_answer: str) -> List:
        """Проверяет ответ для линейного уравнения"""
        correct_answer = self.answer_linear_equation(task)

        user_ans = str(user_answer).strip().rstrip('.0')
        correct_ans = correct_answer.rstrip('.0')

        is_correct = str(user_ans).strip() == correct_ans

        message = "Верно. Продолжайте в том же духе." if is_correct else "Неверно. Проверьте расчеты и попробуйте позже."
        return [message, is_correct, 'linear_equation']

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

        return 's', 1  # fallback

    def answer_for_all_stages(self, task: str) -> str:
        """Находит решение для любого примера"""
        task_type, stage = self.identify_task_type(task)
        numbers = self.parse_numbers(task)

        result = self.OPERATIONS[task_type](numbers)

        # Форматирование результата
        if stage == 1 and task_type in ['s', 'm', 'mul']:
            result = int(round(result))
        else:
            result = round(result, 2)
            if result.is_integer():
                result = int(result)

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
