from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo

from ..lang import WORDINGS


class SignupForm(FlaskForm):
    email = StringField(
        WORDINGS.AUTH.EMAIL,
        validators=[
            DataRequired(WORDINGS.AUTH.INVALID_EMAIL_ADDRESS),
            Length(1, 64),
            Email(message=WORDINGS.AUTH.MISSING_EMAIL_ADDRESS)
        ]
    )
    password = PasswordField(
        WORDINGS.AUTH.PASSWORD,
        validators=[
            DataRequired(message=WORDINGS.COMMON.MISSING_FIELD),
            Length(min=8, message=WORDINGS.AUTH.INVALID_PASSWORD)
        ]
    )
    username = StringField(
        WORDINGS.AUTH.USERNAME,
        validators=[
            DataRequired(message=WORDINGS.COMMON.MISSING_FIELD),
            Length(1, 64)
        ]
    )
    anti_bot = StringField()


class LoginForm(FlaskForm):
    username = StringField(
        WORDINGS.AUTH.USERNAME,
        validators=[
            DataRequired(message=WORDINGS.COMMON.MISSING_FIELD)
        ]
    )
    password = PasswordField(
        WORDINGS.AUTH.PASSWORD,
        validators=[
            DataRequired(message=WORDINGS.COMMON.MISSING_FIELD)
        ]
    )
    remember_me = BooleanField(
        WORDINGS.AUTH.REMEMBER_ME,
        default=False
    )


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(
        WORDINGS.AUTH.CURRENT_PASSWORD,
        validators=[
            DataRequired()
        ]
    )
    password = PasswordField(
        WORDINGS.AUTH.NEW_PASSWORD,
        validators=[
            DataRequired(message=WORDINGS.COMMON.MISSING_FIELD),
            Length(min=8, message=WORDINGS.AUTH.INVALID_PASSWORD),
            EqualTo('password2', message=WORDINGS.AUTH.PASSWORDS_DO_NOT_MATCH)
        ]
    )
    password2 = PasswordField(
        WORDINGS.AUTH.CONFIRM_NEW_PASWORD,
        validators=[
            DataRequired()
        ]
    )


class PasswordResetRequestForm(FlaskForm):
    email = StringField(
        WORDINGS.AUTH.EMAIL,
        validators=[
            DataRequired(),
            Length(1, 64),
            Email()
        ]
    )


class PasswordResetForm(FlaskForm):
    email = StringField(
        WORDINGS.AUTH.EMAIL,
        validators=[
            DataRequired(),
            Length(1, 64),
            Email()
        ]
    )
    password = PasswordField(
        WORDINGS.AUTH.NEW_PASSWORD,
        validators=[
            DataRequired(),
            Length(min=8, message=WORDINGS.AUTH.INVALID_PASSWORD),
            EqualTo("password2", message=WORDINGS.AUTH.PASSWORDS_DO_NOT_MATCH)
        ]
    )
    password2 = PasswordField(
        WORDINGS.AUTH.CONFIRM_NEW_PASWORD,
        validators=[
            DataRequired()
        ]
    )
