from datetime import datetime
from data.db_session import SqlAlchemyBase
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship


class HomeworkSolution(SqlAlchemyBase):
    __tablename__ = 'homework_solutions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    homework_id = Column(Integer, ForeignKey('homeworks.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    group_id = Column(Integer, ForeignKey('groups.id'))
    description = Column(Text, nullable=True)
    points_awarded = Column(Integer, default=0)
    teacher_comment = Column(Text, nullable=True)
    is_graded = Column(Integer, default=False)  # 0 - не оценено, 1 - оценено
    submitted_at = Column(DateTime, default=datetime.now)

    homework = relationship("Homework")
    user = relationship("User")
    group = relationship("Group")
    files = relationship("HomeworkSolutionFile", back_populates="solution", cascade="all, delete-orphan")


class HomeworkSolutionFile(SqlAlchemyBase):
    __tablename__ = 'homework_solution_files'

    id = Column(Integer, primary_key=True, autoincrement=True)
    solution_id = Column(Integer, ForeignKey('homework_solutions.id'))
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.now)

    solution = relationship("HomeworkSolution", back_populates="files")
