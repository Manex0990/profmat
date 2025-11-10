from random import randint, uniform
from typing import List, Tuple
import re


class MyMath:
    def __init__(self):
        self.OPERATORS = {'+': 's',
                          '-': 'm',
                          '*': 'mul',
                          ':': 'cr'}

    def generate_random_numbers(self):
        a, b, c = 0, 0, 0
        while a == 0:
            a = randint(-9, 9)
        while b == 0:
            b = randint(-9, 9)
        while c == 0:
            c = randint(-9, 9)
        return a, b, c

    def format_equation_term(self, coeff: int, variable: str = '', is_first: bool = False) -> str:
        """Форматирует коэффициент уравнения"""
        if coeff == 0:
            return ""

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

    def generate_quadratic_equation(self) -> str:
        """Генерирует квадратное уравнение в строковом формате"""
        a, b, c = self.generate_random_numbers()

        # Формируем уравнение
        equation = self.format_equation_term(a, 'x²', True)
        equation += self.format_equation_term(b, 'x')
        equation += self.format_equation_term(c)

        return f"{equation} = 0"

    def find_coofs_quadratic_equation(self, quadratic_equation: str) -> List[int]:
        a = b = c = 0

        # Убираем пробелы и "= 0"
        equation = quadratic_equation.replace(' ', '').replace('=0', '')

        # Шаблоны для поиска
        x2_pattern = r'([+-]?\d*)x²'  # x²
        x_pattern = r'([+-]?\d*)x(?!²)'  # x
        const_pattern = r'([+-]?\d+)(?!.*x)'

        # Ищем коэффициент перед x²
        x2_match = re.search(x2_pattern, equation)
        if x2_match:
            coeff = x2_match.group(1)
            if not coeff or coeff == '+':
                a = 1
            elif coeff == '-':
                a = -1
            else:
                a = int(coeff)

        # Ищем коэффициент перед x
        x_match = re.search(x_pattern, equation)
        if x_match:
            coeff = x_match.group(1)
            if not coeff or coeff == '+':
                b = 1
            elif coeff == '-':
                b = -1
            else:
                b = int(coeff)

        # Ищем свободный член кв. ур.
        const_match = re.search(const_pattern, equation)
        if const_match:
            c = int(const_match.group(1))

        return [a, b, c]

    def find_discriminant(self, quadratic_equation: str) -> float:
        """Вычисляет дискриминант квадратного уравнения"""
        a, b, c = self.find_coofs_quadratic_equation(quadratic_equation)
        return b ** 2 - 4 * a * c

    def answer_quadratic_equation(self, quadratic_equation: str) -> str:
        """Находит корни квадратного уравнения"""
        a, b, c = self.find_coofs_quadratic_equation(quadratic_equation)
        d = self.find_discriminant(quadratic_equation)

        if d < 0:
            return "Корней нет"
        elif d == 0:
            x = -b / (2 * a)
            return str(int(x) if x.is_integer() else round(x, 2))
        else:
            x1 = (-b - d ** 0.5) / (2 * a)
            x2 = (-b + d ** 0.5) / (2 * a)

            x1 = int(x1) if x1.is_integer() else round(x1, 2)
            x2 = int(x2) if x2.is_integer() else round(x2, 2)

            answers = sorted([x1, x2])
            return ' '.join(str(x) for x in answers)

    def check_answer_quadratic_equation(self, task: str, user_answer: str) -> List:
        """Проверяет ответ для квадратного уравнения"""
        correct_answer = self.answer_quadratic_equation(task)
        is_correct = str(user_answer).strip() == correct_answer

        message = "Верно. Продолжайте в том же духе." if is_correct else "Неверно. Проверьте расчёты и попробуйте еще раз."
        return [message, is_correct, 'square_x']

    def generate_linear_equation(self) -> str:
        """Генерирует линейное уравнение"""
        a, b, c = self.generate_random_numbers()

        left_side = self.format_equation_term(a, 'x', True)
        left_side += self.format_equation_term(b)

        return f"{left_side} = {c}"

    def answer_linear_equation(self, line_x: str) -> str:
        """Находит корень линейного уравнения"""
        # Упрощенная реализация - нужно доработать парсинг
        parts = line_x.split()
        a_str = parts[0].replace('x', '')
        a = 1 if a_str == '' else -1 if a_str == '-' else int(a_str)

        b_sign = 1 if parts[1] == '+' else -1
        b = b_sign * int(parts[2])

        c = int(parts[4])

        x = (c - b) / a
        return str(int(x) if x.is_integer() else round(x, 2))

    def check_answer_linear_equation(self, task: str, user_answer: str) -> List:
        """Проверяет ответ для линейного уравнения"""
        correct_answer = self.answer_linear_equation(task)

        user_ans = str(user_answer).strip().rstrip('.0')
        correct_ans = correct_answer.rstrip('.0')

        is_correct = str(user_ans).strip() == correct_ans

        message = "Верно. Продолжайте в том же духе." if is_correct else "Неверно. Проверьте расчеты и попробуйте позже."
        return [message, is_correct, 'line_x']

    def parse_numbers(self, task: str) -> List[float]:
        """Парсит числа из строки задачи"""
        import re
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

        operations = {'s': sum,
                      'm': lambda nums: nums[0] - sum(nums[1:]),
                      'mul': lambda nums: self.product(nums),
                      'cr': lambda nums: self.divide_sequence(nums)}

        result = operations[task_type](numbers)

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
        result = 1
        for num in numbers:
            result *= num
        return result

    def divide_sequence(self, numbers: List[float]) -> float:
        """Вычисляет последовательное деление"""
        result = numbers[0]
        for num in numbers[1:]:
            result /= num
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
