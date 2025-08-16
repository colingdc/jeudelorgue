from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Optional

from ..domain import does_player_exist


class CreatePlayerForm(FlaskForm):
    first_name = StringField(
        _l("player_first_name"),
        validators=[
            Optional()
        ]
    )
    last_name = StringField(
        _l("player_last_name"),
        validators=[
            DataRequired(message=_l("missing_field"))
        ]
    )

    def validate(self, extra_validators=None):
        rv = FlaskForm.validate(self, extra_validators)
        if not rv:
            return False

        if does_player_exist(self.first_name.data, self.last_name.data):
            self.first_name.errors.append("")
            self.last_name.errors.append(_l("player_already_exists"))
            return False

        return True
