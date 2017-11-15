# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField, IntegerField, SubmitField
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
