import sqlalchemy
from sqlalchemy.orm import relationship

from data.db_session import SqlAlchemyBase


class GroupMember(SqlAlchemyBase):
    __tablename__ = 'group_members'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    group_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("groups.id"))
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    is_teacher = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    points = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    group = relationship("Group", back_populates="members")
    user = relationship("User", back_populates="group_members")