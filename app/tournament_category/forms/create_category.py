from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired

from ..domain import does_category_exist
from ...lang import WORDINGS


class CreateCategoryForm(FlaskForm):
    name = StringField(
        WORDINGS.TOURNAMENT.NAME,
        validators=[
            DataRequired(message=WORDINGS.COMMON.MISSING_FIELD)
        ]
    )
    number_rounds = IntegerField(
        WORDINGS.TOURNAMENT.NUMBER_OF_ROUNDS,
        validators=[
            DataRequired(message=WORDINGS.COMMON.MISSING_FIELD)
        ]
    )
    maximal_score = IntegerField(
        WORDINGS.TOURNAMENT.NUMBER_OF_POINTS_MAX,
        validators=[
            DataRequired(message=WORDINGS.COMMON.MISSING_FIELD)
        ]
    )
    minimal_score = IntegerField(
        validators=[
            DataRequired(message=WORDINGS.COMMON.MISSING_FIELD)
        ]
    )

    def validate(self, extra_validators=None):
        rv = FlaskForm.validate(self, extra_validators)
        if not rv:
            return False

        if does_category_exist(self.name.data):
            self.name.errors.append(WORDINGS.TOURNAMENT.CATEGORY_ALREADY_EXISTS)
            return False

        return True
