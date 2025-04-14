from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, ValidationError, Optional

from ..models import User, Role
from ..texts import VALIDATION, EMAIL_ALREADY_TAKEN, USERNAME_ALREADY_TAKEN


class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(),
                                             Length(1, 64),
                                             Email()])
    username = StringField('Pseudo', validators=[DataRequired(),
                                                 Length(1, 64)])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    submit = SubmitField(VALIDATION)

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)

        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError(EMAIL_ALREADY_TAKEN)

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError(USERNAME_ALREADY_TAKEN)


class ContactForm(FlaskForm):
    email = StringField(u'Email (si vous souhaitez recevoir une réponse)', validators=[Optional(),
                                                                                       Length(1, 64),
                                                                                       Email()])
    message = TextAreaField("Message *", validators=[DataRequired(), Length(max=1000)])
    anti_bot = StringField()
    submit = SubmitField(VALIDATION)
