import sqlalchemy
from .db_session import SqlAlchemyBase


class Towns(SqlAlchemyBase):
    __tablename__ = 'towns'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)