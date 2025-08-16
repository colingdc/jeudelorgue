from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import PasswordField
from wtforms.validators import DataRequired, Length, EqualTo

from ...lang import WORDINGS


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(
        _l("current_password"),
        validators=[
            DataRequired()
        ]
    )
    password = PasswordField(
        _l("new_password"),
        validators=[
            DataRequired(message=WORDINGS.COMMON.MISSING_FIELD),
            Length(min=8, message=WORDINGS.AUTH.INVALID_PASSWORD),
            EqualTo('password2', message=WORDINGS.AUTH.PASSWORDS_DO_NOT_MATCH)
        ]
    )
    password2 = PasswordField(
        _l("confirm_new_password"),
        validators=[
            DataRequired()
        ]
    )
