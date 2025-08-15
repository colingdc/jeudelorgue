from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired

from ..domain import does_category_exist
from ...lang import WORDINGS


class EditCategoryForm(FlaskForm):
    name = StringField(
        WORDINGS.TOURNAMENT.CATEGORY_NAME,
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
        WORDINGS.TOURNAMENT.NUMBER_OF_POINTS_MIN,
        validators=[
            DataRequired(message=WORDINGS.COMMON.MISSING_FIELD)
        ]
    )

    def __init__(self, category, *args, **kwargs):
        super(EditCategoryForm, self).__init__(*args, **kwargs)
        self.category = category

    def validate(self, extra_validators=None):
        rv = FlaskForm.validate(self, extra_validators)
        if not rv:
            return False

        if not self.has_name_changed():
            return True

        if does_category_exist(self.name.data):
            self.name.errors.append(WORDINGS.TOURNAMENT.CATEGORY_ALREADY_EXISTS)
            return False

        return True

    def has_name_changed(self):
        return self.name.data != self.category["name"]
