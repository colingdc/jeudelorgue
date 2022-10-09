# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from ..lang import WORDINGS


class SignupForm(FlaskForm):
    email = StringField(
        'Email',
        validators=[
            DataRequired(WORDINGS.AUTH.INVALID_EMAIL_ADDRESS),
            Length(1, 64),
            Email(message=WORDINGS.AUTH.MISSING_EMAIL_ADDRESS)
        ]
    )
    password = PasswordField(
        'Mot de passe',
        validators=[
            DataRequired(message=WORDINGS.COMMON.MISSING_FIELD),
            Length(min=8, message=WORDINGS.AUTH.INVALID_PASSWORD)
        ]
    )
    username = StringField(
        "Pseudo",
        validators=[
            DataRequired(message=WORDINGS.COMMON.MISSING_FIELD),
            Length(1, 64)
        ]
    )
    submit = SubmitField(WORDINGS.COMMON.VALIDATION)


class LoginForm(FlaskForm):
    username = StringField(
        "Pseudo",
        validators=[
            DataRequired(message=WORDINGS.COMMON.MISSING_FIELD)
        ]
    )
    password = PasswordField(
        "Mot de passe",
        validators=[
            DataRequired(message=WORDINGS.COMMON.MISSING_FIELD)
        ]
    )
    remember_me = BooleanField(
        "Se souvenir de moi",
        default=False
    )
    submit = SubmitField(WORDINGS.COMMON.VALIDATION)


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(
        "Mot de passe actuel",
        validators=[
            DataRequired()
        ]
    )
    password = PasswordField(
        "Nouveau mot de passe",
        validators=[
            DataRequired(message=WORDINGS.COMMON.MISSING_FIELD),
            Length(min=8, message=WORDINGS.AUTH.INVALID_PASSWORD),
            EqualTo('password2', message="Les mots de passe entrés sont différents")
        ]
    )
    password2 = PasswordField(
        "Confirmer le nouveau mot de passe",
        validators=[
            DataRequired()
        ]
    )
    submit = SubmitField(WORDINGS.COMMON.VALIDATION)


class PasswordResetRequestForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Length(1, 64),
            Email()
        ]
    )
    submit = SubmitField(WORDINGS.COMMON.VALIDATION)


class PasswordResetForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Length(1, 64),
            Email()
        ]
    )
    password = PasswordField(
        "Nouveau mot de passe",
        validators=[
            DataRequired(),
            Length(min=8, message=WORDINGS.AUTH.INVALID_PASSWORD),
            EqualTo("password2", message="Les mots de passe entrés sont différents")
        ]
    )
    password2 = PasswordField(
        "Confirmer le mot de passe",
        validators=[
            DataRequired()
        ]
    )
    submit = SubmitField(WORDINGS.COMMON.VALIDATION)
