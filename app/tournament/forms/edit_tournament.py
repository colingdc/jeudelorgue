from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateTimeField
from wtforms.validators import DataRequired, InputRequired, Optional


class EditTournamentForm(FlaskForm):
    name = StringField(
        _l("tournament_name"),
        validators=[
            DataRequired(message=_l("missing_field"))
        ]
    )
    tournament_topic_url = StringField(
        _l("tournament_url_jvc"),
        validators=[
            Optional()
        ]
    )
    jeudelorgue_topic_url = StringField(
        _l("tournament_url_jdl_jvc"),
        validators=[
            Optional()
        ]
    )
    category = SelectField(
        _l("tournament_category"),
        coerce=int,
        validators=[
            Optional()
        ]
    )
    surface = SelectField(
        _l("tournament_surface"),
        coerce=int,
        validators=[
            Optional()
        ]
    )
    start_date = DateTimeField(
        _l("tournament_start_date"),
        format="%d/%m/%Y %H:%M",
        validators=[
            InputRequired(message=_l("missing_field"))
        ]
    )

    def __init__(self, tournament, *args, **kwargs):
        super(EditTournamentForm, self).__init__(*args, **kwargs)
        self.tournament = tournament 
