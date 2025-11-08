from random import randint, uniform

from flask import make_response, render_template


class MyMath:
    def __init__(self):
        pass

    def generate_square_x(self):
        """
        Вернет кв уравнение в строковом формате.
        """
        a_sq = randint(-3, 5)
        if a_sq == 0:
            while a_sq == 0:
                a_sq = randint(-3, 5)
        b_sq = randint(-9, 9)
        c_sq = randint(-9, 9)
        if b_sq == 0:
            b_sq = 1
        elif c_sq == 0:
            c_sq = 1

        if b_sq == 1:
            if c_sq < 0 and a_sq != 1 and a_sq != -1:
                return f'{a_sq}x\u00B2 + x - {-c_sq} = 0'
            elif c_sq < 0 and a_sq == -1:
                return f'-x\u00B2 + x - {-c_sq} = 0'
            elif c_sq < 0 and a_sq == 1:
                return f'x\u00B2 + x - {-c_sq} = 0'
            elif c_sq > 0 and a_sq != 1 and a_sq != -1:
                return f'{a_sq}x\u00B2 + x + {c_sq} = 0'
            elif c_sq > 0 and a_sq == -1:
                return f'-x\u00B2 + x + {c_sq} = 0'
            elif c_sq > 0 and a_sq == 1:
                return f'x\u00B2 + x + {c_sq} = 0'

        elif b_sq == -1:
            if c_sq < 0 and a_sq != 1 and a_sq != -1:
                return f'{a_sq}x\u00B2 - x - {-c_sq} = 0'
            elif c_sq < 0 and a_sq == -1:
                return f'-x\u00B2 - x - {-c_sq} = 0'
            elif c_sq < 0 and a_sq == 1:
                return f'x\u00B2 - x - {-c_sq} = 0'
            elif c_sq > 0 and a_sq != 1 and a_sq != -1:
                return f'{a_sq}x\u00B2 - x + {c_sq} = 0'
            elif c_sq > 0 and a_sq == -1:
                return f'-x\u00B2 - x + {c_sq} = 0'
            elif c_sq > 0 and a_sq == 1:
                return f'x\u00B2 - x + {c_sq} = 0'

        else:
            if b_sq > 0:
                if c_sq < 0 and a_sq != 1 and a_sq != -1:
                    return f'{a_sq}x\u00B2 + {b_sq}x - {-c_sq} = 0'
                elif c_sq < 0 and a_sq == -1:
                    return f'-x\u00B2 + {b_sq}x - {-c_sq} = 0'
                elif c_sq < 0 and a_sq == 1:
                    return f'x\u00B2 + {b_sq}x - {-c_sq} = 0'
                elif c_sq > 0 and a_sq != 1 and a_sq != -1:
                    return f'{a_sq}x\u00B2 + {b_sq}x + {c_sq} = 0'
                elif c_sq > 0 and a_sq == -1:
                    return f'-x\u00B2 + {b_sq}x + {c_sq} = 0'
                elif c_sq > 0 and a_sq == 1:
                    return f'x\u00B2 + {b_sq}x + {c_sq} = 0'
            elif b_sq < 0:
                if c_sq < 0 and a_sq != 1 and a_sq != -1:
                    return f'{a_sq}x\u00B2 - {-b_sq}x - {-c_sq} = 0'
                elif c_sq < 0 and a_sq == -1:
                    return f'-x\u00B2 - {-b_sq}x - {-c_sq} = 0'
                elif c_sq < 0 and a_sq == 1:
                    return f'x\u00B2 - {-b_sq}x - {-c_sq} = 0'
                elif c_sq > 0 and a_sq != 1 and a_sq != -1:
                    return f'{a_sq}x\u00B2 - {-b_sq}x + {c_sq} = 0'
                elif c_sq > 0 and a_sq == -1:
                    return f'-x\u00B2 - {-b_sq}x + {c_sq} = 0'
                elif c_sq > 0 and a_sq == 1:
                    return f'x\u00B2 - {-b_sq}x + {c_sq} = 0'

    def find_coofs_square_x(self, square_x):
        coofs = []
        if square_x.startswith('-'):
            a_sq = -1
        elif square_x.startswith('x'):
            a_sq = 1
        else:
            for i in square_x:
                if i != '\u00B2' and i.isdigit() and int(i) != 0:
                    coofs.append(i)
            a_sq = int(coofs[0])

        square_x = square_x.split()
        if square_x[1] == '-' and square_x[2] == 'x':
            b_sq = -1
        elif square_x[1] == '+' and square_x[2] == 'x':
            b_sq = 1
        else:
            if square_x[1] == '-':
                b_sq = -int(square_x[2][0])
            elif square_x[1] == '+':
                b_sq = int(square_x[2][0])

        if square_x[3] == '-':
            c_sq = -int(square_x[4])
        elif square_x[3] == '+':
            c_sq = int(square_x[4])
        return [a_sq, b_sq, c_sq]

    def answer_square_x(self, square_x):
        """
        Вернет 1) если дискриминант положительный - список из 2 целых или дробных чисел
                  2) если дискриминант 0 - одно целое или дробное число
                  3) если дискриминант отрицательный - строку "Корней нет"
           корни последнего сгенерированного кв уравнения
           """
        coofs = self.find_coofs_square_x(square_x)
        a_sq, b_sq, c_sq = coofs[0], coofs[1], coofs[2]
        d = (abs(b_sq) ** 2) - (4 * a_sq * c_sq)
        if d == 0:
            answer = (-b_sq) / (2 * a_sq)
            if int(answer) == answer:
                answer = int(answer)
            elif int(answer) != answer:
                answer = round(answer, 2)
            return str(answer)

        elif d > 0:
            x1 = (-b_sq - d ** 0.5) / (2 * a_sq)
            x2 = (-b_sq + d ** 0.5) / (2 * a_sq)
            if int(x1) == x1 and int(x2) != x2:
                answer = sorted([int(x1), round(x2, 2)])
            elif int(x1) != x1 and int(x2) == x2:
                answer = sorted([round(x1, 2), int(x2)])
            elif int(x1) == x1 and int(x2) == x2:
                answer = sorted([int(x1), int(x2)])
            elif int(x1) != x1 and int(x2) != x2:
                answer = sorted([round(x1, 2), round(x2, 2)])
            for i in range(len(answer)):
                answer[i] = str(answer[i])
            return ' '.join(answer)

        else:
            answer = 'Корней нет'
            return answer

    def find_discriminant(self, square_x):
        coofs = self.find_coofs_square_x(square_x)
        a_sq, b_sq, c_sq = coofs[0], coofs[1], coofs[2]
        d = (abs(b_sq) ** 2) - (4 * a_sq * c_sq)
        return d

    def check_answer_square_x(self, task, user_answer):
        """
        В качестве ответа может быть принято
        1) 2 корня кв уравнения через пробел(это могут быть целые числа или дробные(округлите до сотых) числа)
        2) один корень - целое чило или дробное(округлите до сотых) число
        3) строка 'Корней нет'
        """
        if str(user_answer) == str(self.answer_square_x(task)):
            return ['Верно. Продолжайте в том же духе.', True, 'square_x']
        else:
            return ['Неверно. Проверьте расчёты и попробуйте еще раз.', False]

    def generate_line_x(self):
        """
        Вернет линейное уравнение в строковом формате
        """
        a_li = randint(-9, 9)
        if a_li == 0:
            a_li = 1
        b_li = randint(-9, 9)
        c_li = randint(-9, 9)
        if c_li == 0:
            c_li = 1

        if b_li < 0:
            line_x = f'{a_li}x - {-b_li} = {c_li}'
        elif b_li > 0:
            line_x = f'{a_li}x + {b_li} = {c_li}'
        elif b_li == 0:
            b_li = 1
            line_x = f'{a_li}x + {b_li} = {c_li}'

        if a_li == 1:
            line_x = line_x[1:]
        elif a_li == -1:
            line_x = f'-{line_x[2:]}'
        return line_x

    def answer_line_x(self, line_x):
        """
        Вернет корень последнего сгенерированного линейного уравнения
        """
        line_x = line_x.split()
        if line_x[0][0] == '-' and line_x[0][1] == 'x':
            a_li = -1
        elif line_x[0] == 'x':
            a_li = 1
        else:
            if line_x[0][0] == '-':
                a_li = -int(line_x[0][1])
            else:
                a_li = int(line_x[0][0])

        if line_x[1] == '-':
            b_li = -int(line_x[2])
        elif line_x[1] == '+':
            b_li = int(line_x[2])

        c_li = int(line_x[-1])

        temp_x = c_li + (-b_li)
        if temp_x / a_li == temp_x // a_li:
            x = int(temp_x / a_li)
        else:
            x = round(temp_x / a_li, 2)
        return str(x)

    def check_answer_line_x(self, task, user_answer):
        """
        В качестве ответа может быть принято
        целое число или дробное(округлите до сотых) число
        """
        if str(user_answer) == str(self.answer_line_x(task)):
            return ['Верно. Продолжайте в том же духе.', True, 'line_x']
        else:
            return [f'Неверно. Проверьте расчеты и попробуйте позже.', False]

    def search_coofs_for_stage_1_2(self, task):
        """
        Находит коэффициенты примеров простого и среднего уровня сложности.
        """
        task = task.split()
        coofs = [float(task[0]), float(task[2])]
        return coofs

    def search_coofs_for_stage_3(self, task):
        """
        Находит коэффициенты примеров сложного уровня сложности.
        """
        task = task.split()
        coofs = [int(task[0]), float(task[2]), float(task[4]), int(task[6])]
        return coofs

    def iddentificate_task(self, task):
        """
        Узнает тип примера и уровень.
        """
        task = task.split()
        stage = 0

        if len(task) == 5:
            if task[0].isdigit() and task[2].isdigit():
                stage = 1
            elif ((len(task[0]) == 3 or len(task[0]) == 4 or len(task[0]) == 5) or
                  (len(task[2]) == 3 or len(task[2]) == 4 or len(task[0]) == 5)):
                stage = 2
        elif len(task) == 9:
            stage = 3

        data = {'+': 's', '-': 'm', '*': 'mul', ':': 'cr'}
        type_task = data[task[1]]

        return [type_task, str(stage)]

    def answer_for_all_stages(self, task):
        """
        Находит решение на любой пример всех сложностей.
        """
        type_task = self.iddentificate_task(task)[0]
        stage = int(self.iddentificate_task(task)[1])
        if type_task == 's':
            if stage == 1:
                a, b = self.search_coofs_for_stage_1_2(task)
                return str(int(a + b))
            elif stage == 2:
                a, b = self.search_coofs_for_stage_1_2(task)
                return str(round(a + b, 2))
            elif stage == 3:
                a, b, c, d = self.search_coofs_for_stage_3(task)
                return str(round(a + b + c + d, 2))
        elif type_task == 'm':
            if stage == 1:
                a, b = self.search_coofs_for_stage_1_2(task)
                return str(int(a - b))
            elif stage == 2:
                a, b = self.search_coofs_for_stage_1_2(task)
                return str(round(a - b, 2))
            elif stage == 3:
                a, b, c, d = self.search_coofs_for_stage_3(task)
                return str(round(a - b - c - d, 2))
        elif type_task == 'cr':
            if stage == 1:
                a, b = self.search_coofs_for_stage_1_2(task)
                return str(round(a / b, 2))
            elif stage == 2:
                a, b = self.search_coofs_for_stage_1_2(task)
                return str(round(a / b, 2))
            elif stage == 3:
                a, b, c, d = self.search_coofs_for_stage_3(task)
                return str(round(a / b / c / d, 2))
        elif type_task == 'mul':
            if stage == 1:
                a, b = self.search_coofs_for_stage_1_2(task)
                return str(int(round(a * b, 2)))
            elif stage == 2:
                a, b = self.search_coofs_for_stage_1_2(task)
                return str(round(a * b, 2))
            elif stage == 3:
                a, b, c, d = self.search_coofs_for_stage_3(task)
                return str(round(a * b * c * d, 2))

    def check_answer_for_all_stages(self, task, user_answer):
        """
        Проверить ответ пользователя на любой пример.
        """
        type_task = '_'.join(self.iddentificate_task(task))
        ans = self.answer_for_all_stages(task)
        if ans[-2:] == '.0':
            ans = ans[:-2]
        if user_answer[-2:] == '.0':
            user_answer = user_answer[:-2]
        if str(user_answer) == str(ans):
            return ['Верно. Продолжайте в том же духе.', True, type_task]
        else:
            return ['Неверно. Проверьте рассчеты и попробуйте позже.', False]

    def generate_sum_stage_1(self):
        """
        Вернет пример на сложение простого уровня сложности в строковом формате
        """
        a_s_1 = randint(1, 101)
        b_s_1 = randint(1, 101)
        return f'{a_s_1} + {b_s_1} = ?'

    def generate_sum_stage_2(self):
        """
        Вернет пример на сложение среднего уровня сложности в строковом формате
        """
        a_s_2 = round(uniform(1, 20), 2)
        b_s_2 = round(uniform(1, 20), 2)
        return f'{a_s_2} + {b_s_2} = ?'

    def generate_sum_stage_3(self):
        """
        Вернет пример на сложение высокого уровня сложности в строковом формате
        """
        a_s_3 = randint(1, 30)
        b_s_3 = round(uniform(1, 30), 2)
        c_s_3 = round(uniform(1, 30), 2)
        d_s_3 = randint(1, 30)
        return f'{a_s_3} + {b_s_3} + {c_s_3} + {d_s_3} = ?'

    def generate_min_stage_1(self):
        """
        Вернет пример на вычитание простого уровня сложности в строковом формате
        """
        a_m_1 = randint(1, 101)
        b_m_1 = randint(1, 101)
        return f'{a_m_1} - {b_m_1} = ?'

    def generate_min_stage_2(self):
        """
        Вернет пример на вычитание среднего уровня сложности в строковом формате
        """
        a_m_2 = round(uniform(1, 20), 2)
        b_m_2 = round(uniform(1, 20), 2)
        return f'{a_m_2} - {b_m_2} = ?'

    def generate_min_stage_3(self):
        """
        Вернет пример на вычитание высокого уровня сложности в строковом формате
        """
        a_m_3 = randint(50, 100)
        b_m_3 = round(uniform(30, 50), 2)
        c_m_3 = round(uniform(20, 30), 2)
        d_m_3 = randint(1, 20)
        return f'{a_m_3} - {b_m_3} - {c_m_3} - {d_m_3} = ?'

    def generate_crop_stage_1(self):
        """
        Вернет пример на деление в строковом формате
        """
        a_cr_1 = randint(1, 51)
        b_cr_1 = randint(1, 51)
        return f'{a_cr_1} : {b_cr_1} = ?'

    def generate_crop_stage_2(self):
        """
        Вернет пример на деление среднего уровня сложности в строковом формате
        """
        a_cr_2 = round(uniform(1, 20), 2)
        b_cr_2 = round(uniform(1, 20), 2)
        return f'{a_cr_2} : {b_cr_2} = ?'

    def generate_crop_stage_3(self):
        """
        Вернет пример на деление высокого уровня сложности в строковом формате
        """
        a_cr_3 = randint(10, 40)
        b_cr_3 = round(uniform(1, 8), 1)
        c_cr_3 = round(uniform(1, 6), 1)
        d_cr_3 = randint(1, 4)
        return f'{a_cr_3} : {b_cr_3} : {c_cr_3} : {d_cr_3} = ?'

    def generate_multiply_stage_1(self):
        """
        Вернет пример на умножение в строковом формате
        """
        a_mul_1 = randint(1, 21)
        b_mul_1 = randint(1, 21)
        return f'{a_mul_1} * {b_mul_1} = ?'

    def generate_multiply_stage_2(self):
        """
        Вернет пример на умножение среднего уровня сложности в строковом формате
        """
        a_mul_2 = round(uniform(1, 10), 2)
        b_mul_2 = round(uniform(1, 10), 2)
        return f'{a_mul_2} * {b_mul_2} = ?'

    def generate_multiply_stage_3(self):
        """
        Вернет пример на умножение высокого уровня сложности в строковом формате
        """
        a_mul_3 = randint(1, 10)
        b_mul_3 = round(uniform(1, 10), 2)
        c_mul_3 = round(uniform(1, 10), 2)
        d_mul_3 = randint(1, 10)
        return f'{a_mul_3} * {b_mul_3} * {c_mul_3} * {d_mul_3} = ?'
