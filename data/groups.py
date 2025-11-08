import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy.orm import relationship
import uuid


class Group(SqlAlchemyBase):
    __tablename__ = 'groups'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    invite_link = sqlalchemy.Column(sqlalchemy.String, unique=True, default=lambda: str(uuid.uuid4()))
    members = relationship("GroupMember", back_populates="group")

    def __repr__(self):
        return f'<Group> {self.id} {self.name}'
