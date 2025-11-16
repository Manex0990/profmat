from maths import MyMath

ex = MyMath()
TASK_CONFIG = {'biquadratic_equation': {'name': 'Биквадратное уравнение',
                                        'generate_func': ex.generate_biquadratic_equation,
                                        'check_func': ex.check_answer_biquadratic_equation,
                                        'points': 30,
                                        'get_solution': lambda task: [
                                            'Для начала сделаем замену: y = x²'
                                            f'{task.replace('x⁴', 'y²').replace('x²', 'y')}'
                                            'Теперь найдем дискриминант полученного квадратного уравнения:',
                                            'Если дискриминант больше нуля, то будет 2 корня',
                                            'Если равен нулю, то будет 1 корень',
                                            'Если меньше нуля, то корней нет.',
                                            f'a = {ex.find_coofs_quadratic_equation(task)[0]}',
                                            f'b = {ex.find_coofs_quadratic_equation(task)[1]}',
                                            f'c = {ex.find_coofs_quadratic_equation(task)[2]}',
                                            f'D = b² - 4ac; D = {ex.find_discriminant(task)}',
                                            *(['Теперь можно найти корни уравнения:',
                                               'y₁ = (-b - √D) / 2a',
                                               f'y₁ = {ex.answer_quadratic_equation(task).split()[0]}',
                                               'y₂ = (-b + √D) / 2a',
                                               f'y₂ = {ex.answer_quadratic_equation(task).split()[1]}',
                                               'Сделаем обратную подстановку: ',
                                               f'x² = {ex.answer_quadratic_equation(task).split()[0]} или x² = {ex.answer_quadratic_equation(task).split()[1]}',
                                               'Извлечем квадратный корень из обоих частей каждого уравнения' ]
                                              if ex.find_discriminant(task) > 0 else
                                              ['Теперь можно найти корень уравнения:',
                                               'y = -b / 2a', f'y = {ex.answer_quadratic_equation(task)}',
                                               f'Ответ: {ex.answer_quadratic_equation(task)}']
                                              if ex.find_discriminant(task) == 0 else
                                              ['Так как дискриминант меньше нуля, корней нет',
                                               'Ответ: корней нет'])
                                        ]},
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
