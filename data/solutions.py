import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from datetime import datetime

class Solution(SqlAlchemyBase):
    __tablename__ = 'solutions'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    task_type = sqlalchemy.Column(sqlalchemy.String, nullable=False)  # тип задачи
    task_content = sqlalchemy.Column(sqlalchemy.Text, nullable=False)  # задача
    user_answer = sqlalchemy.Column(sqlalchemy.Text, nullable=False)   # ответ пользователя
    correct_answer = sqlalchemy.Column(sqlalchemy.Text, nullable=False) # правильный ответ
    is_correct = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)  # верно ли решено
    points_awarded = sqlalchemy.Column(sqlalchemy.Integer, default=0)   # сколько баллов начислено
    submitted_at = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now)

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    group_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('groups.id'))

    user = orm.relationship('User')
    group = orm.relationship('Group')
    files = orm.relationship("SolutionFile", back_populates="solution", cascade="all, delete-orphan")