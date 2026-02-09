from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, MultipleFileField
from wtforms import TextAreaField, SubmitField, IntegerField
from wtforms.validators import Optional, DataRequired


class HomeworkSolutionForm(FlaskForm):
    description = TextAreaField('Комментарий к решению', validators=[Optional()])
    files = MultipleFileField('Файлы с решением', validators=[
        FileAllowed(['pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx', 'txt', 'zip', 'rar', 'pptx', 'ppt'],
                    'Допустимые форматы: PDF, PNG, JPG, DOC, PPT, TXT, ZIP, RAR')
    ])
    submit = SubmitField('Отправить решение')


class GradeHomeworkForm(FlaskForm):
    points = IntegerField('Баллы', validators=[DataRequired()])
    comment = TextAreaField('Комментарий учителя', validators=[Optional()])
    submit = SubmitField('Сохранить оценку')
