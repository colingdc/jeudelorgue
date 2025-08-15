from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired

from ...lang import WORDINGS
from ...models import TournamentCategory


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
        if (self.name.data != self.category["name"]
                and (TournamentCategory.query.filter_by(name=self.name.data).first())):
            self.name.errors.append(WORDINGS.TOURNAMENT.CATEGORY_ALREADY_EXISTS)
            return False
        return True 
