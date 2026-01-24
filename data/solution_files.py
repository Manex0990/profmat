from datetime import datetime
from data.db_session import SqlAlchemyBase
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship


class SolutionFile(SqlAlchemyBase):
    __tablename__ = 'solution_files'

    id = Column(Integer, primary_key=True, autoincrement=True)
    solution_id = Column(Integer, ForeignKey('solutions.id'))
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.now)

    solution = relationship("Solution", back_populates="files")