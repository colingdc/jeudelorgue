# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField, IntegerField, SubmitField, SelectField, FormField, FieldList
from wtforms.validators import DataRequired, InputRequired


class CreateTournamentForm(FlaskForm):
    name = StringField('Nom',
                       validators = [DataRequired(message = "Ce champ est obligatoire")])
    number_rounds = IntegerField('Nombre de tours',
                                 validators = [DataRequired(message = "Ce champ est obligatoire")])
    start_date = DateTimeField(u'Date de début',
                               format = "%d/%m/%Y %H:%M",
                               validators = [InputRequired(message = "Ce champ est obligatoire")])
    submit = SubmitField("Valider")


class EditTournamentForm(FlaskForm):
    name = StringField('Nom',
                       validators = [DataRequired(message = "Ce champ est obligatoire")])
    number_rounds = IntegerField('Nombre de tours',
                                 validators = [DataRequired(message = "Ce champ est obligatoire")])
    start_date = DateTimeField(u'Date de début',
                               format = "%d/%m/%Y %H:%M",
                               validators = [InputRequired(message = "Ce champ est obligatoire")])
    submit = SubmitField("Valider")

    def __init__(self, tournament, *args, **kwargs):
        super(EditTournamentForm, self).__init__(*args, **kwargs)
        self.tournament = tournament


class PlayerTournamentDrawForm(FlaskForm):
    player_name = SelectField("Joueur", coerce = int)
    status = SelectField("Statut", coerce = int)
    seed = IntegerField(u"Tête de série")


class CreateTournamentDrawForm(FlaskForm):
    player = FieldList(FormField(PlayerTournamentDrawForm))
    submit = SubmitField("Valider")
