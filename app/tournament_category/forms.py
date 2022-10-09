# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired

from ..models import TournamentCategory
from ..lang import WORDINGS


class CreateCategoryForm(FlaskForm):
    name = StringField(
        u"Nom",
        validators=[
            DataRequired(message=WORDINGS.COMMON.MISSING_FIELD)
        ]
    )
    number_rounds = IntegerField(
        u"Nombre de tours",
        validators=[
            DataRequired(message=WORDINGS.COMMON.MISSING_FIELD)
        ]
    )
    maximal_score = IntegerField(
        u"Nombre de points du vainqueur",
        validators=[
            DataRequired(message=WORDINGS.COMMON.MISSING_FIELD)
        ]
    )
    minimal_score = IntegerField(
        u"Nombre de points du dernier participant",
        validators=[
            DataRequired(message=WORDINGS.COMMON.MISSING_FIELD)
        ]
    )
    submit = SubmitField("Valider")

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False
        if (TournamentCategory.query.filter_by(name=self.name.data).first()):
            self.name.errors.append(WORDINGS.TOURNAMENT.CATEGORY_ALREADY_EXISTS)
            return False
        return True


class EditCategoryForm(FlaskForm):
    name = StringField(
        u"Nom",
        validators=[
            DataRequired(message=WORDINGS.COMMON.MISSING_FIELD)
        ]
    )
    number_rounds = IntegerField(
        u"Nombre de tours",
        validators=[
            DataRequired(message=WORDINGS.COMMON.MISSING_FIELD)
        ]
    )
    maximal_score = IntegerField(
        u"Nombre de points du vainqueur",
        validators=[
            DataRequired(message=WORDINGS.COMMON.MISSING_FIELD)
        ]
    )
    minimal_score = IntegerField(
        u"Nombre de points du dernier participant",
        validators=[
            DataRequired(message=WORDINGS.COMMON.MISSING_FIELD)
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
            self.name.errors.append(WORDINGS.TOURNAMENT.CATEGORY_ALREADY_EXISTS)
            return False
        return True
