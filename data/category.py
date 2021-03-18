import sqlalchemy
from .db_session import SqlAlchemyBase


class Categories(SqlAlchemyBase):
    __tablename__ = 'category'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)