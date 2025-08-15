from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo

from ...lang import WORDINGS


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
