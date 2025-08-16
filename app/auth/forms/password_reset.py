from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class PasswordResetForm(FlaskForm):
    email = StringField(
        _l("email"),
        validators=[
            DataRequired(),
            Length(1, 64),
            Email()
        ]
    )
    password = PasswordField(
        _l("new_password"),
        validators=[
            DataRequired(),
            Length(min=8, message=_l("invalid_password")),
            EqualTo("password2", message=_l("passwords_do_not_match"))
        ]
    )
    password2 = PasswordField(
        _l("confirm_new_password"),
        validators=[
            DataRequired()
        ]
    ) 
