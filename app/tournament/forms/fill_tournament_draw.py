from flask_wtf import FlaskForm
from wtforms import StringField


class FillTournamentDrawForm(FlaskForm):
    forecast = StringField("forecast") 
