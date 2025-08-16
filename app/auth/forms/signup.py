from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, Length

from ...lang import WORDINGS


class SignupForm(FlaskForm):
    email = StringField(
        _l("email"),
        validators=[
            DataRequired(WORDINGS.AUTH.INVALID_EMAIL_ADDRESS),
            Length(1, 64),
            Email(message=WORDINGS.AUTH.MISSING_EMAIL_ADDRESS)
        ]
    )
    password = PasswordField(
        _l("password"),
        validators=[
            DataRequired(message=WORDINGS.COMMON.MISSING_FIELD),
            Length(min=8, message=WORDINGS.AUTH.INVALID_PASSWORD)
        ]
    )
    username = StringField(
        _l("username"),
        validators=[
            DataRequired(message=WORDINGS.COMMON.MISSING_FIELD),
            Length(1, 64)
        ]
    )
    anti_bot = StringField() 
