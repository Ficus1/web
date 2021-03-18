import flask
from flask import jsonify, request, render_template
from flask_login import login_required, current_user
from werkzeug.exceptions import abort
from werkzeug.utils import redirect

from .adverts import Adverts
from web_pr.data import db_session
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, BooleanField, IntegerField, SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired

blueprint = flask.Blueprint(
    'advert_api',
    __name__,
    template_folder='templates'
)

