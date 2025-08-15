from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length, Email

from ...lang import WORDINGS


class PasswordResetRequestForm(FlaskForm):
    email = StringField(
        WORDINGS.AUTH.EMAIL,
        validators=[
            DataRequired(),
            Length(1, 64),
            Email()
        ]
    ) 
