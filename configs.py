from maths import MyMath

ex = MyMath()
TASK_CONFIG = {'quadratic_equation': {'name': 'Квадратное уравнение',
                          'generate_func': ex.generate_quadratic_equation,
                          'check_func': ex.check_answer_quadratic_equation,
                          'points': 20,
                          'get_solution': lambda task: [
                              'Сначала найдем дискриминант квадратного уравнения:',
                              'Если дискриминант больше нуля, то будет 2 корня',
                              'Если равен нулю, то будет 1 корень',
                              'Если меньше нуля, то корней нет.',
                              f'D = b² - 4ac; D = {ex.find_discriminant(task)}',
                              'Теперь можно найти корни(корень) уравнения',
                              'x1 = (-b - √D) / 2a',
                              'x2 = (-b + √D) / 2a',
                              f'Ответ: {ex.answer_quadratic_equation(task)}']},
               'linear_equation': {'name': 'Линейное уравнение',
                        'generate_func': ex.generate_linear_equation,
                        'check_func': ex.check_answer_linear_equation,
                        'points': 15,
                        'get_solution': lambda task:
                        ['Для того, чтобы решить линейное уравнение нужно все коэффициенты с "х"',
                         'перенести в одну часть уравнения, а остальные в другую.',
                         f'Ответ: {ex.answer_linear_equation(task)}']}}

OPERATIONS_CONFIG = {'sum': {'sum': 'сложим', 'name': 'Пример на сложение', 'points': [5, 8, 10]},
                   'min': {'min': 'вычтем', 'name': 'Пример на вычитание', 'points': [5, 8, 10]},
                   'mul': {'mul': 'перемножим', 'name': 'Пример на умножение', 'points': [7, 10, 12]},
                   'crop': {'crop': 'разделим', 'name': 'Пример на деление', 'points': [10, 12, 15]}}