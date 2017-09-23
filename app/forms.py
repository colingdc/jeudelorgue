# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField("Pseudo",
                           validators = [DataRequired(message = "Ce champ est obligatoire")])
    password = PasswordField('Mot de passe',
                             validators = [DataRequired(message = "Ce champ est obligatoire")])
    remember_me = BooleanField("Se souvenir de moi",
                               default = False)
    submit = SubmitField("Valider")
