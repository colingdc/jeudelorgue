from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import SelectField


class RankingForm(FlaskForm):
    tournament_name = SelectField(
        _l("tournament"),
        coerce=int
    )
    ranking_type = SelectField(
        _l("ranking_type"),
        choices=[
            ("race", _l("race_ranking")),
            ("annual", _l("annual_ranking"))
        ]
    ) 
