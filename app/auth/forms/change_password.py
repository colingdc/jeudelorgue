from flask_wtf import FlaskForm
from wtforms import PasswordField
from wtforms.validators import DataRequired, Length, EqualTo

from ...lang import WORDINGS


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
