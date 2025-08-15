from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional

from ...lang import WORDINGS


class ContactForm(FlaskForm):
    email = StringField(
        WORDINGS.AUTH.EMAIL,
        validators=[
            Optional(),
            Length(1, 64),
            Email()
        ]
    )
    message = TextAreaField(
        WORDINGS.MAIN.MESSAGE,
        validators=[
            DataRequired(),
            Length(max=1000)
        ]
    ) 
