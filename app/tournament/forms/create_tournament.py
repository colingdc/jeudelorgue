from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateTimeField
from wtforms.validators import DataRequired, InputRequired, Optional

from ...lang import WORDINGS


class CreateTournamentForm(FlaskForm):
    name = StringField(
        WORDINGS.TOURNAMENT.NAME,
        validators=[
            DataRequired(message=WORDINGS.COMMON.MISSING_FIELD)
        ]
    )
    tournament_topic_url = StringField(
        WORDINGS.TOURNAMENT.URL_JVC,
        validators=[
            Optional()
        ]
    )
    jeudelorgue_topic_url = StringField(
        WORDINGS.TOURNAMENT.URL_JDL_JVC,
        validators=[
            Optional()
        ]
    )
    category = SelectField(
        WORDINGS.TOURNAMENT.CATEGORY,
        coerce=int
    )
    surface = SelectField(
        WORDINGS.TOURNAMENT.SURFACE,
        coerce=int
    )
    start_date = DateTimeField(
        WORDINGS.TOURNAMENT.START_DATE,
        format="%d/%m/%Y %H:%M",
        validators=[
            InputRequired(message=WORDINGS.COMMON.MISSING_FIELD)
        ]
    ) 
