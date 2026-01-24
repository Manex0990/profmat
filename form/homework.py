from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField, TextAreaField


class HomeworkForm(FlaskForm):
    description = TextAreaField('Описание задания')
    file = FileField('Файл задания', validators=[
        FileRequired(),
        FileAllowed(['pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx', 'txt', 'zip', 'rar'],
                   'Допустимые форматы: PDF, PNG, JPG, DOC, TXT, ZIP, RAR')
    ])
    submit = SubmitField('Загрузить задание')