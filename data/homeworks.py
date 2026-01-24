from datetime import datetime
from data.db_session import SqlAlchemyBase
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship


class Homework(SqlAlchemyBase):
    __tablename__ = 'homeworks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey('groups.id'))
    user_id = Column(Integer, ForeignKey('users.id'))  # учитель, который добавил
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    group = relationship("Group")
    teacher = relationship("User")