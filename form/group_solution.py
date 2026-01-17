from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SubmitField
from wtforms.validators import Optional
from wtforms.widgets import DateInput


class GroupSolutionsForm(FlaskForm):
    surname = StringField('Фамилия', validators=[Optional()])
    name = StringField('Имя', validators=[Optional()])
    patronymic = StringField('Отчество', validators=[Optional()])
    date = DateField(
        'Дата решения',
        validators=[Optional()],
        widget=DateInput(),
        format='%Y-%m-%d'
    )
    submit = SubmitField('Найти')
    show_all = SubmitField('Показать все')
    clean = SubmitField('Очистить историю')
