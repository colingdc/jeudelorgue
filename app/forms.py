# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from .texts import MISSING_FIELD
from .texts import MISSING_EMAIL_ADDRESS, INVALID_EMAIL_ADDRESS
from .texts import INVALID_PASSWORD
from .texts import VALIDATION


class SignupForm(FlaskForm):
    email = StringField('Email', validators = [DataRequired(INVALID_EMAIL_ADDRESS),
                                               Email(message = MISSING_EMAIL_ADDRESS)])
    password = PasswordField('Mot de passe', validators = [DataRequired(message = MISSING_FIELD),
                                                           Length(min = 6, message = INVALID_PASSWORD)])
    username = StringField("Pseudo", validators = [DataRequired(message = MISSING_FIELD)])
    submit = SubmitField(VALIDATION)


class LoginForm(FlaskForm):
    username = StringField("Pseudo", validators = [DataRequired(message = MISSING_FIELD)])
    password = PasswordField("Mot de passe", validators = [DataRequired(message = MISSING_FIELD)])
    remember_me = BooleanField("Se souvenir de moi", default = False)
    submit = SubmitField(VALIDATION)
