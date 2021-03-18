import sqlalchemy
from .db_session import SqlAlchemyBase


class Adverts(SqlAlchemyBase):
    __tablename__ = 'adverts'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    price = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    town = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    photo = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    address = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    category = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("category.id"))
    member = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))