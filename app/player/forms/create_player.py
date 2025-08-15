from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Optional

from ...lang import WORDINGS
from ...models import Player


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
        if (Player.query.filter_by(first_name=self.first_name.data)
                .filter_by(last_name=self.last_name.data).first()):
            self.first_name.errors.append("")
            self.last_name.errors.append(WORDINGS.PLAYER.PLAYER_ALREADY_EXISTS)
            return False
        return True 
