from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import SelectField


class TournamentPlayerStatsForm(FlaskForm):
    player_name = SelectField(
        _l("tournament_stats_order_draw"),
        coerce=int
    )


class TournamentPlayerAlphabeticStatsForm(FlaskForm):
    player_name = SelectField(
        _l("tournament_stats_order_alphabetical"),
        coerce=int
    ) 
