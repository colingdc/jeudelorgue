# -*- coding: utf-8 -*-

import datetime
import pandas as pd
from flask import current_app, url_for
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from . import db, bcrypt, login_manager


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key = True)
    deleted_at = db.Column(db.DateTime, default = None)
    created_at = db.Column(db.DateTime, default = datetime.datetime.now)
    confirmed = db.Column(db.Boolean, default = False)
    username = db.Column(db.String(64), index = True, unique = True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    email = db.Column(db.String(120), index = True, unique = True)
    password_hash = db.Column(db.String(128))

    participants = db.relationship("Participant", backref = "user", lazy = "dynamic")

    def __repr__(self):
        return "<User %r>" % self.username

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        if self.role is None:
            if self.email == current_app.config['ADMIN_JDL']:
                self.role = Role.query.filter_by(permissions = 0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default = True).first()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password)

    def verify_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def can(self, permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def is_manager(self):
        return self.can(Permission.MANAGE_TOURNAMENT)

    def generate_confirmation_token(self, expiration = 3600):
        s = Serializer(current_app.config["SECRET_KEY"], expiration)
        return s.dumps({"confirm": self.id})

    def generate_reset_token(self, expiration = 3600):
        s = Serializer(current_app.config["SECRET_KEY"], expiration)
        return s.dumps({"reset": self.id})

    def confirm(self, token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get("confirm") != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get("reset") != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def get_id(self):
        return str(self.id)

    def get_participant(self, tournament_id):
        return (Participant.query
                .filter(Participant.tournament_id == tournament_id)
                .filter(Participant.user_id == self.id)
                ).first()

    def is_registered_to_tournament(self, tournament_id):
        return self.get_participant(tournament_id) is not None


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

    def is_manager(self):
        return False


login_manager.anonymous_user = AnonymousUser


class Permission:
    PARTICIPATE_TOURNAMENT = 0x01
    MANAGE_TOURNAMENT = 0x02
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), unique = True)
    default = db.Column(db.Boolean, default = False, index = True)
    permissions = db.Column(db.Integer)
    users = db.relationship("User", backref = "role", lazy = "dynamic")

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.PARTICIPATE_TOURNAMENT, True),
            'Tournament Manager': (Permission.PARTICIPATE_TOURNAMENT |
                                   Permission.MANAGE_TOURNAMENT,
                                   False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name = r).first()
            if role is None:
                role = Role(name = r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class TournamentStatus:
    CREATED = 10
    REGISTRATION_OPEN = 20
    ONGOING = 30
    FINISHED = 40


class Tournament(db.Model):
    __tablename__ = "tournaments"
    id = db.Column(db.Integer, primary_key = True)
    created_at = db.Column(db.DateTime, default = datetime.datetime.now)
    deleted_at = db.Column(db.DateTime, default = None)

    name = db.Column(db.String(64))
    number_rounds = db.Column(db.Integer)
    started_at = db.Column(db.DateTime)
    ended_at = db.Column(db.DateTime, default = None)
    status = db.Column(db.Integer, default = TournamentStatus.CREATED)

    participants = db.relationship("Participant", backref = "tournament", lazy = "dynamic")
    players = db.relationship("TournamentPlayer", backref = "tournament", lazy = "dynamic")

    def is_open_to_registration(self):
        return self.status == TournamentStatus.REGISTRATION_OPEN

    def is_visible(self):
        return self.status >= TournamentStatus.REGISTRATION_OPEN

    def get_participants(self):
        query = (User.query
                 .join(Participant)
                 .with_entities(User.id, User.username, Participant.created_at)
                 .filter(Participant.tournament_id == self.id)
                 .all())
        df = pd.DataFrame(query)

        try:
            df.columns = [u"id", u"Pseudo", u"Date d'inscription"]
            df["Tableau"] = df["id"].apply(lambda x: url_for("tournament.view_participant_draw",
                                                             tournament_id = self.id,
                                                             user_id = x,
                                                             _external = True))
            del df["id"]
            return df
        except ValueError:
            df = pd.DataFrame(columns = [u"Pseudo", u"Date d'inscription", u"Tableau"])
            return df


class Participant(db.Model):
    __tablename__ = "participants"
    id = db.Column(db.Integer, primary_key = True)
    created_at = db.Column(db.DateTime, default = datetime.datetime.now)
    deleted_at = db.Column(db.DateTime, default = None)
    matches_not_forecasted = db.Column(db.Integer, default = None)

    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    forecasts = db.relationship("Forecast", backref = "participant", lazy = "dynamic")


class Player(db.Model):
    __tablename__ = "players"
    id = db.Column(db.Integer, primary_key = True)
    created_at = db.Column(db.DateTime, default = datetime.datetime.now)
    deleted_at = db.Column(db.DateTime, default = None)

    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))

    def get_full_name(self):
        return u"{} {}".format(self.first_name.capitalize(), self.last_name.upper())


class TournamentPlayer(db.Model):
    __tablename__ = "tournament_players"
    id = db.Column(db.Integer, primary_key = True)
    created_at = db.Column(db.DateTime, default = datetime.datetime.now)
    deleted_at = db.Column(db.DateTime, default = None)

    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'))
    position = db.Column(db.Integer)
    matches_won = db.relationship("Match", backref = "tournament_player", lazy = "dynamic")


class Match(db.Model):
    __tablename__ = "matches"
    id = db.Column(db.Integer, primary_key = True)
    created_at = db.Column(db.DateTime, default = datetime.datetime.now)
    deleted_at = db.Column(db.DateTime, default = None)

    position = db.Column(db.Integer)
    score = db.Column(db.String(64))

    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'))
    winner_id = db.Column(db.Integer, db.ForeignKey('tournament_players.id'))
    tournament_player1_id = db.Column(db.Integer)
    tournament_player2_id = db.Column(db.Integer)


class Forecast(db.Model):
    __tablename__ = "forecasts"
    id = db.Column(db.Integer, primary_key = True)
    created_at = db.Column(db.DateTime, default = datetime.datetime.now)
    deleted_at = db.Column(db.DateTime, default = None)

    match_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'))
    winner_id = db.Column(db.Integer, db.ForeignKey('tournament_players.id'))
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'))
