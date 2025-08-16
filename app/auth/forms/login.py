from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField
from wtforms.validators import DataRequired

from ...lang import WORDINGS


class LoginForm(FlaskForm):
    username = StringField(
        _l("username"),
        validators=[
            DataRequired(message=WORDINGS.COMMON.MISSING_FIELD)
        ]
    )
    password = PasswordField(
        _l("password"),
        validators=[
            DataRequired(message=WORDINGS.COMMON.MISSING_FIELD)
        ]
    )
    remember_me = BooleanField(
        _l("remember_me"),
        default=False
    )
