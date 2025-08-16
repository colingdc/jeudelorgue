from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired, Optional

from ..domain import does_category_exist


class EditCategoryForm(FlaskForm):
    name = StringField(
        _l("tournament_category_name"),
        validators=[
            DataRequired(message=_l("missing_field"))
        ]
    )
    number_rounds = IntegerField(
        _l("tournament_number_of_rounds"),
        validators=[
            Optional()
        ]
    )
    maximal_score = IntegerField(
        _l("tournament_number_of_points_max"),
        validators=[
            DataRequired(message=_l("missing_field"))
        ]
    )
    minimal_score = IntegerField(
        _l("tournament_number_of_points_min"),
        validators=[
            DataRequired(message=_l("missing_field"))
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
            self.name.errors.append(_l("tournament_category_already_exists"))
            return False

        return True

    def has_name_changed(self):
        return self.name.data != self.category["name"]
