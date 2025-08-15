from flask_wtf import FlaskForm
from wtforms import SelectField

from ...lang import WORDINGS


class RankingForm(FlaskForm):
    tournament_name = SelectField(
        WORDINGS.TOURNAMENT.TOURNAMENT,
        coerce=int
    )
    ranking_type = SelectField(
        WORDINGS.RANKING.RANKING_TYPE,
        choices=[
            ("race", WORDINGS.RANKING.RACE_RANKING),
            ("annual", WORDINGS.RANKING.ANNUAL_RANKING)
        ]
    ) 
