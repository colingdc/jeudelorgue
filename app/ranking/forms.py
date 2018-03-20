# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, RadioField
from wtforms.validators import DataRequired, InputRequired, Optional


class RankingForm(FlaskForm):
    tournament_name = SelectField("Tournoi", coerce = int)
    ranking_type = SelectField("Type de classement", choices = [("race", "Race"), ("annual", "Annuel")])
