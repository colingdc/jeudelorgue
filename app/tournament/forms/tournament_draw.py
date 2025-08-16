from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, IntegerField, FieldList, FormField
from wtforms.validators import Optional


class PlayerTournamentDrawForm(FlaskForm):
    player1_name = SelectField(_l("player"), coerce=int)
    player2_name = SelectField(_l("player"), coerce=int)
    player1_status = StringField(_l("player_status"))
    player2_status = StringField(_l("player_status"))
    player1_seed = IntegerField(_l("player_seed"), validators=[Optional()])
    player2_seed = IntegerField(_l("player_seed"), validators=[Optional()])


class CreateTournamentDrawForm(FlaskForm):
    player = FieldList(FormField(PlayerTournamentDrawForm)) 
