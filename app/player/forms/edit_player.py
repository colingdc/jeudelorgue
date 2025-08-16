from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Optional

from ..domain import does_player_exist
from ...lang import WORDINGS


class EditPlayerForm(FlaskForm):
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

    def __init__(self, player, *args, **kwargs):
        super(EditPlayerForm, self).__init__(*args, **kwargs)
        self.player = player

    def validate(self, extra_validators=None):
        rv = FlaskForm.validate(self, extra_validators)
        if not rv:
            return False

        if not self.has_first_name_changed() and not self.has_last_name_changed():
            return True

        if does_player_exist(self.first_name.data, self.last_name.data):
            self.first_name.errors.append("")
            self.last_name.errors.append(WORDINGS.PLAYER.PLAYER_ALREADY_EXISTS)
            return False

        return True

    def has_first_name_changed(self):
        return self.first_name.data != self.player["first_name"]

    def has_last_name_changed(self):
        return self.last_name.data != self.player["last_name"]
