from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, Length


class SignupForm(FlaskForm):
    email = StringField(
        _l("email"),
        validators=[
            DataRequired(_l("invalid_email_address")),
            Length(1, 64),
            Email(message=_l("missing_email_address"))
        ]
    )
    password = PasswordField(
        _l("password"),
        validators=[
            DataRequired(message=_l("missing_field")),
            Length(min=8, message=_l("invalid_password"))
        ]
    )
    username = StringField(
        _l("username"),
        validators=[
            DataRequired(message=_l("missing_field")),
            Length(1, 64)
        ]
    )
    anti_bot = StringField() 
