from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class TaskForm(FlaskForm):
    answer = StringField('Ответ', validators=[DataRequired()])
    file = FileField('Прикрепить файл с решением', validators=[
        FileAllowed(['pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx', 'txt', 'zip', 'rar'],
                   'Допустимые форматы: PDF, PNG, JPG, DOC, TXT, ZIP, RAR')
    ])
    submit = SubmitField('Отправить')
