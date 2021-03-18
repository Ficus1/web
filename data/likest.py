import sqlalchemy
from .db_session import SqlAlchemyBase


class Like(SqlAlchemyBase):
    __tablename__ = 'like'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    advert = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("adverts.id"))
    member = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))