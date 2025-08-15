from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField
from wtforms.validators import DataRequired

from ...lang import WORDINGS


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
