from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired

from ..models import TournamentCategory
from ..texts import CATEGORY_ALREADY_EXISTS


class CreateCategoryForm(FlaskForm):
    name = StringField(
        "Nom",
        validators=[
            DataRequired(message="Ce champ est obligatoire")
        ]
    )
    number_rounds = IntegerField(
        "Nombre de tours",
        validators=[
            DataRequired(message="Ce champ est obligatoire")
        ]
    )
    maximal_score = IntegerField(
        "Nombre de points du vainqueur",
        validators=[
            DataRequired(message="Ce champ est obligatoire")
        ]
    )
    minimal_score = IntegerField(
        "Nombre de points du dernier participant",
        validators=[
            DataRequired(message="Ce champ est obligatoire")
        ]
    )
    submit = SubmitField("Valider")

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False
        if (TournamentCategory.query.filter_by(name=self.name.data).first()):
            self.name.errors.append(CATEGORY_ALREADY_EXISTS)
            return False
        return True


class EditCategoryForm(FlaskForm):
    name = StringField(
        "Nom",
        validators=[
            DataRequired(message="Ce champ est obligatoire")
        ]
    )
    number_rounds = IntegerField(
        "Nombre de tours",
        validators=[
            DataRequired(message="Ce champ est obligatoire")
        ]
    )
    maximal_score = IntegerField(
        "Nombre de points du vainqueur",
        validators=[
            DataRequired(message="Ce champ est obligatoire")
        ]
    )
    minimal_score = IntegerField(
        "Nombre de points du dernier participant",
        validators=[
            DataRequired(message="Ce champ est obligatoire")
        ]
    )
    submit = SubmitField("Valider")

    def __init__(self, category, *args, **kwargs):
        super(EditCategoryForm, self).__init__(*args, **kwargs)
        self.category = category

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False
        if (self.name.data != self.category["name"]
                and (TournamentCategory.query.filter_by(name=self.name.data).first())):
            self.name.errors.append(CATEGORY_ALREADY_EXISTS)
            return False
        return True
