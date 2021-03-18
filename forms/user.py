from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, SelectField, IntegerField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email
from cities import cities


class RegisterForm(FlaskForm):

    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    surname = StringField('Фамилия пользователя', validators=[DataRequired()])
    town = SelectField("Ваш город", validators=[DataRequired()], choices=[[i, i] for i in cities])
    age = IntegerField("Ваш возраст", validators=[DataRequired()])
    phone_number = StringField("Номер телефона", validators=[DataRequired()])
    submit = SubmitField('Продолжить')