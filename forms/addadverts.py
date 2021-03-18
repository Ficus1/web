from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, BooleanField, IntegerField, SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class AddAdverts(FlaskForm):
    price = IntegerField('Стоимость', validators=[DataRequired()])
    name = StringField('Название', validators=[DataRequired()])
    description = TextAreaField('Характеристики', validators=[DataRequired()])
    category = SelectField("Категория", validators=[DataRequired()], choices=[[1, 'Электроприборы'], [2, 'Авто'], [3, 'Недвижимость'],
                                                                              [4, 'Работа'], [4, 'Другое']])
    about = TextAreaField('Описание', validators=[DataRequired()])
    address = StringField('Адрес(работы, и т.п), можно оставить пустым')
    submit = SubmitField('Разместить')