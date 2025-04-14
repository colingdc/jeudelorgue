from flask_wtf import FlaskForm
from wtforms import SelectField


class RankingForm(FlaskForm):
    tournament_name = SelectField(
        "Tournoi",
        coerce=int
    )
    ranking_type = SelectField(
        "Type de classement",
        choices=[
            ("race", "Race"),
            ("annual", "Annuel")
        ]
    )
