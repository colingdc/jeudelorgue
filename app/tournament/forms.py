from flask_wtf import FlaskForm
from wtforms import (
    DateTimeField,
    FieldList,
    FormField,
    IntegerField,
    SelectField,
    StringField,
)
from wtforms.validators import (
    DataRequired,
    InputRequired,
    Optional,
)

from ..lang import WORDINGS


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


class EditTournamentForm(FlaskForm):
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
        coerce=int,
        validators=[
            Optional()
        ]
    )
    surface = SelectField(
        WORDINGS.TOURNAMENT.SURFACE,
        coerce=int,
        validators=[
            Optional()
        ]
    )
    start_date = DateTimeField(
        WORDINGS.TOURNAMENT.START_DATE,
        format="%d/%m/%Y %H:%M",
        validators=[
            InputRequired(message=WORDINGS.COMMON.MISSING_FIELD)
        ]
    )

    def __init__(self, tournament, *args, **kwargs):
        super(EditTournamentForm, self).__init__(*args, **kwargs)
        self.tournament = tournament


class PlayerTournamentDrawForm(FlaskForm):
    player1_name = SelectField(WORDINGS.PLAYER.PLAYER, coerce=int)
    player2_name = SelectField(WORDINGS.PLAYER.PLAYER, coerce=int)
    player1_status = StringField(WORDINGS.PLAYER.STATUS)
    player2_status = StringField(WORDINGS.PLAYER.STATUS)
    player1_seed = IntegerField(WORDINGS.PLAYER.SEED, validators=[Optional()])
    player2_seed = IntegerField(WORDINGS.PLAYER.SEED, validators=[Optional()])


class CreateTournamentDrawForm(FlaskForm):
    player = FieldList(FormField(PlayerTournamentDrawForm))


class FillTournamentDrawForm(FlaskForm):
    forecast = StringField("forecast")


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
