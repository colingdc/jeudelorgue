# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

from ..models import Player
from ..texts import PLAYER_ALREADY_EXISTS


class CreatePlayerForm(FlaskForm):
    first_name = StringField(u"Prénom",
                             validators = [DataRequired(message = "Ce champ est obligatoire")])
    last_name = StringField("Nom",
                            validators = [DataRequired(message = "Ce champ est obligatoire")])
    submit = SubmitField("Valider")

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False
        if (Player.query.filter_by(first_name = self.first_name.data)
                        .filter_by(last_name = self.last_name.data).first()):
            self.first_name.errors.append("")
            self.last_name.errors.append(PLAYER_ALREADY_EXISTS)
            return False
        return True


class EditPlayerForm(FlaskForm):
    first_name = StringField(u"Prénom",
                             validators = [DataRequired(message = "Ce champ est obligatoire")])
    last_name = StringField("Nom",
                            validators = [DataRequired(message = "Ce champ est obligatoire")])
    submit = SubmitField("Valider")

    def __init__(self, player, *args, **kwargs):
        super(EditPlayerForm, self).__init__(*args, **kwargs)
        self.player = player

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False
        if (self.first_name.data != self.player.first_name
            and self.last_name.data != self.player.last_name
            and (Player.query.filter_by(first_name = self.first_name.data)
                             .filter_by(last_name = self.last_name.data).first())):
            self.first_name.errors.append("")
            self.last_name.errors.append(PLAYER_ALREADY_EXISTS)
            return False
        return True
