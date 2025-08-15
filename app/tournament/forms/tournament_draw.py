from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, IntegerField, FieldList, FormField
from wtforms.validators import Optional

from ...lang import WORDINGS


class PlayerTournamentDrawForm(FlaskForm):
    player1_name = SelectField(WORDINGS.PLAYER.PLAYER, coerce=int)
    player2_name = SelectField(WORDINGS.PLAYER.PLAYER, coerce=int)
    player1_status = StringField(WORDINGS.PLAYER.STATUS)
    player2_status = StringField(WORDINGS.PLAYER.STATUS)
    player1_seed = IntegerField(WORDINGS.PLAYER.SEED, validators=[Optional()])
    player2_seed = IntegerField(WORDINGS.PLAYER.SEED, validators=[Optional()])


class CreateTournamentDrawForm(FlaskForm):
    player = FieldList(FormField(PlayerTournamentDrawForm)) 
