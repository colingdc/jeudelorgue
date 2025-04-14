from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField, IntegerField, SelectField, FormField, FieldList
from wtforms.validators import DataRequired, InputRequired, Optional


class CreateTournamentForm(FlaskForm):
    name = StringField(
        'Nom',
        validators=[
            DataRequired(message="Ce champ est obligatoire")
        ]
    )
    tournament_topic_url = StringField(
        'Lien du topic du tournoi sur JVC',
        validators=[
            Optional()
        ]
    )
    jeudelorgue_topic_url = StringField(
        'Lien du topic du jeu de L-orgue sur JVC',
        validators=[
            Optional()
        ]
    )
    category = SelectField(
        'Catégorie',
        coerce=int
    )
    surface = SelectField(
        'Surface',
        coerce=int
    )
    start_date = DateTimeField(
        'Date de début',
        format="%d/%m/%Y %H:%M",
        validators=[
            InputRequired(message="Ce champ est obligatoire")
        ]
    )


class EditTournamentForm(FlaskForm):
    name = StringField(
        'Nom',
        validators=[
            DataRequired(message="Ce champ est obligatoire")
        ]
    )
    tournament_topic_url = StringField(
        'Lien du topic du tournoi sur JVC',
        validators=[
            Optional()
        ]
    )
    jeudelorgue_topic_url = StringField(
        'Lien du topic du jeu de L-orgue sur JVC',
        validators=[
            Optional()
        ]
    )
    category = SelectField(
        'Catégorie',
        coerce=int,
        validators=[
            Optional()
        ]
    )
    surface = SelectField(
        'Surface',
        coerce=int,
        validators=[
            Optional()
        ]
    )
    start_date = DateTimeField(
        'Date de début',
        format="%d/%m/%Y %H:%M",
        validators=[
            InputRequired(message="Ce champ est obligatoire")
        ]
    )

    def __init__(self, tournament, *args, **kwargs):
        super(EditTournamentForm, self).__init__(*args, **kwargs)
        self.tournament = tournament


class PlayerTournamentDrawForm(FlaskForm):
    player1_name = SelectField(
        "Joueur",
        coerce=int
    )
    player2_name = SelectField(
        "Joueur",
        coerce=int
    )
    player1_status = StringField("Statut")
    player2_status = StringField("Statut")
    player1_seed = IntegerField(
        "Tête de série",
        validators=[
            Optional()
        ]
    )
    player2_seed = IntegerField(
        "Tête de série",
        validators=[
            Optional()
        ]
    )


class CreateTournamentDrawForm(FlaskForm):
    player = FieldList(FormField(PlayerTournamentDrawForm))


class FillTournamentDrawForm(FlaskForm):
    forecast = StringField("forecast")


class TournamentPlayerStatsForm(FlaskForm):
    player_name = SelectField(
        "Ordre du tableau",
        coerce=int
    )


class TournamentPlayerAlphabeticStatsForm(FlaskForm):
    player_name = SelectField(
        "Ordre alphabétique",
        coerce=int
    )
