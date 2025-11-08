from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SubmitField


class TaskForm(FlaskForm):
    answer = StringField('Ответ')
    submit = SubmitField('Ответить')
