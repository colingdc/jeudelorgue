# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField, IntegerField, SubmitField, SelectField, FormField, FieldList
from wtforms.validators import DataRequired, InputRequired, Optional


class CreateTournamentForm(FlaskForm):
    name = StringField('Nom',
                       validators = [DataRequired(message = "Ce champ est obligatoire")])
    tournament_topic_url = StringField('Lien du topic du tournoi sur JVC',
                                       validators = [Optional()])
    jeudelorgue_topic_url = StringField('Lien du topic du jeu de L-orgue sur JVC',
                                       validators = [Optional()])
    category = SelectField(u'Catégorie', coerce = int)
    surface = SelectField(u'Surface', coerce = int)
    start_date = DateTimeField(u'Date de début',
                               format = "%d/%m/%Y %H:%M",
                               validators = [InputRequired(message = "Ce champ est obligatoire")])
    submit = SubmitField("Valider")


class EditTournamentForm(FlaskForm):
    name = StringField('Nom',
                       validators = [DataRequired(message = "Ce champ est obligatoire")])
    tournament_topic_url = StringField('Lien du topic du tournoi sur JVC',
                                       validators = [Optional()])
    jeudelorgue_topic_url = StringField('Lien du topic du jeu de L-orgue sur JVC',
                                       validators = [Optional()])
    category = SelectField(u'Catégorie', coerce = int,
                           validators = [Optional()])
    surface = SelectField(u'Surface', coerce = int,
                           validators = [Optional()])
    start_date = DateTimeField(u'Date de début',
                               format = "%d/%m/%Y %H:%M",
                               validators = [InputRequired(message = "Ce champ est obligatoire")])
    submit = SubmitField("Valider")

    def __init__(self, tournament, *args, **kwargs):
        super(EditTournamentForm, self).__init__(*args, **kwargs)
        self.tournament = tournament


class PlayerTournamentDrawForm(FlaskForm):
    player1_name = SelectField("Joueur", coerce = int)
    player2_name = SelectField("Joueur", coerce = int)
    player1_status = StringField("Statut")
    player2_status = StringField("Statut")
    player1_seed = IntegerField(u"Tête de série", validators = [Optional()])
    player2_seed = IntegerField(u"Tête de série", validators = [Optional()])


class CreateTournamentDrawForm(FlaskForm):
    player = FieldList(FormField(PlayerTournamentDrawForm))
    submit = SubmitField("Valider")


class FillTournamentDrawForm(FlaskForm):
    forecast = StringField("forecast")
    submit = SubmitField("Valider")


class TournamentPlayerStatsForm(FlaskForm):
    player_name = SelectField("Ordre du tableau", coerce = int)

class TournamentPlayerAlphabeticStatsForm(FlaskForm):
    player_name = SelectField(u"Ordre alphabétique", coerce = int)

class IntermediaryRankingsForm(FlaskForm):
    round_name = SelectField(u"Voir le classement à l'issue...", coerce = int)
