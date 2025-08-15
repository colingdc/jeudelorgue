from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, Length, ValidationError

from ...lang import WORDINGS
from ...models import User, Role


class EditProfileAdminForm(FlaskForm):
    email = StringField(
        WORDINGS.AUTH.EMAIL,
        validators=[
            DataRequired(),
            Length(1, 64),
            Email()
        ]
    )
    username = StringField(
        WORDINGS.AUTH.USERNAME,
        validators=[
            DataRequired(),
            Length(1, 64)
        ]
    )
    confirmed = BooleanField(WORDINGS.MAIN.CONFIRMED)
    role = SelectField(WORDINGS.MAIN.ROLE, coerce=int)

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)

        self.role.choices = [
            (role.id, role.name)
            for role in Role.query.order_by(Role.name).all()
        ]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError(WORDINGS.AUTH.EMAIL_ALREADY_TAKEN)

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError(WORDINGS.AUTH.USERNAME_ALREADY_TAKEN) 
