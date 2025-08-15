from flask_wtf import FlaskForm
from wtforms import SelectField

from ...lang import WORDINGS


class TournamentPlayerStatsForm(FlaskForm):
    player_name = SelectField(
        WORDINGS.TOURNAMENT.ORDER_DRAW,
        coerce=int
    )


class TournamentPlayerAlphabeticStatsForm(FlaskForm):
    player_name = SelectField(
        WORDINGS.TOURNAMENT.ORDER_ALPHABETICAL,
        coerce=int
    ) 
