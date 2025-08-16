from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length, Email


class PasswordResetRequestForm(FlaskForm):
    email = StringField(
        _l("email"),
        validators=[
            DataRequired(),
            Length(1, 64),
            Email()
        ]
    ) 
