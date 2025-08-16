from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired

from ..domain import does_category_exist


class CreateCategoryForm(FlaskForm):
    name = StringField(
        _l("tournament_category_name"),
        validators=[
            DataRequired(message=_l("missing_field"))
        ]
    )
    number_rounds = IntegerField(
        _l("tournament_number_of_rounds"),
        validators=[
            DataRequired(message=_l("missing_field"))
        ]
    )
    maximal_score = IntegerField(
        _l("tournament_number_of_points_max"),
        validators=[
            DataRequired(message=_l("missing_field"))
        ]
    )
    minimal_score = IntegerField(
        validators=[
            DataRequired(message=_l("missing_field"))
        ]
    )

    def validate(self, extra_validators=None):
        rv = FlaskForm.validate(self, extra_validators)
        if not rv:
            return False

        if does_category_exist(self.name.data):
            self.name.errors.append(_l("tournament_category_already_exists"))
            return False

        return True
