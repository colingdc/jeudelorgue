from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Optional

from ..domain import does_player_exist
from ...lang import WORDINGS


class CreatePlayerForm(FlaskForm):
    first_name = StringField(
        WORDINGS.PLAYER.FIRST_NAME,
        validators=[
            Optional()
        ]
    )
    last_name = StringField(
        WORDINGS.PLAYER.LAST_NAME,
        validators=[
            DataRequired(message=WORDINGS.COMMON.MISSING_FIELD)
        ]
    )

    def validate(self, extra_validators=None):
        rv = FlaskForm.validate(self, extra_validators)
        if not rv:
            return False

        if does_player_exist(self.first_name.data, self.last_name.data):
            self.first_name.errors.append("")
            self.last_name.errors.append(WORDINGS.PLAYER.PLAYER_ALREADY_EXISTS)
            return False

        return True
