from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import PasswordField
from wtforms.validators import DataRequired, Length, EqualTo


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
            DataRequired(message=_l("missing_field")),
            Length(min=8, message=_l("invalid_password")),
            EqualTo('password2', message=_l("passwords_do_not_match"))
        ]
    )
    password2 = PasswordField(
        _l("confirm_new_password"),
        validators=[
            DataRequired()
        ]
    )
