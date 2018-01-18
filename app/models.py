# -*- coding: utf-8 -*-

import datetime
from dateutil.relativedelta import relativedelta
from math import log, exp
from flask import current_app, url_for
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from . import db, bcrypt, login_manager
from sqlalchemy import or_, func



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
    annual_points = db.Column(db.Integer)
    year_to_date_points = db.Column(db.Integer)

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

    @staticmethod
    def insert_user(email, role_name, username = None, confirmed = True, password = "test1234"):
        role = Role.query.filter_by(name = role_name).first()
        if role is None:
            print("This role does not exist")
        else:
            if username is None:
                username = email
            user = User(email = email,
                        role = role,
                        confirmed = confirmed,
                        username = username,
                        password = password)
            db.session.add(user)
            db.session.commit()


    def get_id(self):
        return str(self.id)

    def get_participant(self, tournament_id):
        return (Participant.query
                .filter(Participant.tournament_id == tournament_id)
                .filter(Participant.user_id == self.id)
                ).first()

    def is_registered_to_tournament(self, tournament_id):
        return self.get_participant(tournament_id) is not None

    @property
    def year_to_date_participations(self):
        participations = (self.participants
                          .join(Tournament, Tournament.id == Participant.tournament_id)
                          .filter(func.year(Tournament.started_at) == datetime.datetime.now().year)
                          .filter(Tournament.started_at <= datetime.datetime.now()))
        return participations

    @property
    def annual_participations(self):
        participations = (self.participants
                          .join(Tournament, Tournament.id == Participant.tournament_id)
                          .filter(Tournament.started_at >= datetime.datetime.now() - relativedelta(years = 1))
                          .filter(Tournament.started_at <= datetime.datetime.now()))
        return participations

    def get_annual_points(self):
        return sum(participation.points for participation in self.annual_participations if participation.points is not None)

    def get_year_to_date_points(self):
        return sum(participation.points for participation in self.annual_participations if participation.points is not None)

    def participants_sorted(self):
        return (self.participants.order_by(Participant.created_at.desc()))


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
    started_at = db.Column(db.DateTime)
    ended_at = db.Column(db.DateTime, default = None)
    status = db.Column(db.Integer, default = TournamentStatus.CREATED)
    category_id = db.Column(db.Integer, db.ForeignKey("tournament_categories.id"))
    category = db.relationship("TournamentCategory", foreign_keys = category_id)

    matches = db.relationship("Match", backref = "tournament", lazy = "dynamic")
    participants = db.relationship("Participant", backref = "tournament", lazy = "dynamic")
    players = db.relationship("TournamentPlayer", backref = "tournament", lazy = "dynamic")

    def is_open_to_registration(self):
        return self.status == TournamentStatus.REGISTRATION_OPEN

    def is_visible(self):
        return self.status >= TournamentStatus.REGISTRATION_OPEN

    def is_ongoing(self):
        return self.status == TournamentStatus.ONGOING

    def is_finished(self):
        return self.status >= TournamentStatus.FINISHED

    def get_matches_first_round(self):
        return [m for m in self.matches if m.round == self.number_rounds]

    def get_matches_by_round(self):
        return [{"round": i,
                 "matches": self.matches.filter(Match.round == i).all(),
                 "first_round": i == self.number_rounds}
                for i in range(self.number_rounds, 0, -1)]

    def is_draw_created(self):
        return TournamentPlayer.query.filter(TournamentPlayer.tournament_id == self.id).first() is not None

    def get_last_match(self):
        return self.matches.filter(Match.position == 1).first()

    def are_draws_private(self):
        return self.status < TournamentStatus.ONGOING

    @property
    def number_rounds(self):
        return self.category.number_rounds

    def get_round_names(self):
        names = ["F", "DF", "QF", "HF"]
        if self.number_rounds > 4:
            names += ["T" + str(i) for i in range(self.number_rounds - 4, 0, -1)]
            return names[::-1]
        else:
            return names[:self.number_rounds][::-1]

    def get_score_per_round(self):
        if self.number_rounds < 7:
            return {round: 2 ** (self.number_rounds - round)
                    for round in range(1, self.number_rounds + 1)}
        return {round: 2 ** (self.number_rounds - round - 1) if round < self.number_rounds else 1
                for round in range(1, self.number_rounds + 1)}

    def get_current_maximal_score(self):
        score_per_round = self.get_score_per_round()
        score = 0
        for match in self.matches:
            if match.winner_id:
                match_score = score_per_round[match.round]
                score += match_score
        return score

    def participants_sorted(self):
        return (self.participants.order_by(Participant.score.desc(), Participant.risk_coefficient))

    def get_tournament_player_stats(self, tournament_player):
        # Get the tournament player's first round match
        first_match = (self.matches.filter(or_(Match.tournament_player1_id == tournament_player.id,
                                               Match.tournament_player2_id == tournament_player.id))
                                   .filter(Match.round == self.number_rounds)).first()
        if not first_match:
            return None

        stats = {}
        for round in range(1, self.number_rounds + 1):
            position = first_match.position // 2 ** (self.number_rounds - round)
            match = self.matches.filter(Match.position == position)

            round_stats = {f.participant: f.winner
                           for f in match.first().forecasts}
            stats[round] = round_stats

        return stats

    def get_overall_forecasts_stats(self):
        stats = {}
        forecasts = (Forecast.query
                     .join(Match, Match.id == Forecast.match_id)
                     .filter(Match.tournament_id == self.id))

        for tournament_player in self.players:
            stats[tournament_player] = {}
            for round in range(1, self.number_rounds + 1):
                 stats[tournament_player][round] = (forecasts
                                                   .filter(Match.round == round)
                                                   .filter(Forecast.winner_id == tournament_player.id)
                                                   .count())

        self.overall_forecasts_stats = stats
        return stats

    def distribute_points(self):
        participants = self.participants.order_by(Participant.score.desc(), Participant.risk_coefficient, Participant.created_at)
        alpha = self.category.maximal_score
        if self.participants.count() > 1:
            beta = (log(self.category.minimal_score) - log(self.category.maximal_score)) / log(self.participants.count())
        else:
            beta = 1
        scores = {participant: round(alpha * (rank + 1) ** beta) for rank, participant in enumerate(participants)}
        return scores

    @classmethod
    def get_current_tournament(cls):
        return cls.query.filter(cls.ended_at == None).order_by(cls.started_at.desc()).first()

    @classmethod
    def get_recent_tournaments(cls, number_tournaments):
        return cls.query.order_by(cls.started_at.desc()).limit(number_tournaments)



class TournamentCategory(db.Model):
    __tablename__ = "tournament_categories"
    id = db.Column(db.Integer, primary_key = True)
    created_at = db.Column(db.DateTime, default = datetime.datetime.now)
    deleted_at = db.Column(db.DateTime, default = None)

    name = db.Column(db.String(64))
    number_rounds = db.Column(db.Integer)
    maximal_score = db.Column(db.Integer)
    minimal_score = db.Column(db.Integer)

    @classmethod
    def get_all_categories(cls):
        return [(p.id, p.name) for p in cls.query.order_by(cls.name).all()]


class Participant(db.Model):
    __tablename__ = "participants"
    id = db.Column(db.Integer, primary_key = True)
    created_at = db.Column(db.DateTime, default = datetime.datetime.now)
    deleted_at = db.Column(db.DateTime, default = None)
    matches_not_forecasted = db.Column(db.Integer, default = None)
    score = db.Column(db.Integer, default = 0)
    risk_coefficient = db.Column(db.Integer, default = 0)
    points = db.Column(db.Integer, default = 0)
    ranking = db.Column(db.Integer, default = None)

    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    forecasts = db.relationship("Forecast", backref = "participant", lazy = "dynamic")

    def has_filled_draw(self):
        return len(self.forecasts.all()) > 0

    def get_score(self):
        score_per_round = self.tournament.get_score_per_round()
        score = 0
        for forecast in self.forecasts:
            result = forecast.match
            if result.winner_id:
                match_score = (result.winner_id == forecast.winner_id) * score_per_round[result.round]
                score += match_score
        return score

    def get_risk_coefficient(self):
        score_per_round = self.tournament.get_score_per_round()

        my_forecasts = self.forecasts
        coeffs = {forecast.match.id: 0 for forecast in my_forecasts}
        other_participants_forecasts = [p.forecasts for p in self.tournament.participants if p.id != self.id]

        for other_participant_forecasts in other_participants_forecasts:
            for my_forecast, other_participant_forecast in zip(my_forecasts.order_by(Forecast.match_id), other_participant_forecasts.order_by(Forecast.match_id)):
                coeffs[my_forecast.match.id] = (my_forecast.winner_id == other_participant_forecast.winner_id) * score_per_round[my_forecast.match.round]

        return sum(coeffs.values())


class Player(db.Model):
    __tablename__ = "players"
    id = db.Column(db.Integer, primary_key = True)
    created_at = db.Column(db.DateTime, default = datetime.datetime.now)
    deleted_at = db.Column(db.DateTime, default = None)

    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))

    tournament_players = db.relationship("TournamentPlayer", backref = "player", lazy = "dynamic")

    def get_full_name(self):
        return u"{} {}".format(self.first_name,
                                  self.last_name.upper())

    def get_draw_name(self):
        if self.first_name:
            return u"{} {}".format(self.first_name[0] + ".",
                                      self.last_name.upper())
        else:
            return self.last_name.upper()


    def get_full_name_surname_first(self):
        return u"{}, {}".format(self.last_name.upper(), self.first_name)

    @classmethod
    def get_all_players(cls):
        return [(p.id, p.get_full_name_surname_first())
        for p in cls.query.filter(cls.deleted_at.is_(None))
        .order_by(cls.last_name, cls.first_name).all()]


class TournamentPlayer(db.Model):
    __tablename__ = "tournament_players"
    id = db.Column(db.Integer, primary_key = True)
    created_at = db.Column(db.DateTime, default = datetime.datetime.now)
    deleted_at = db.Column(db.DateTime, default = None)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'))

    seed = db.Column(db.Integer)
    status = db.Column(db.String(8))

    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'))
    position = db.Column(db.Integer)
    matches_won = db.relationship("Match",
                                  backref = "winner_tournament_player",
                                  primaryjoin = "TournamentPlayer.id==Match.winner_id",
                                  lazy = "dynamic")
    matches = db.relationship("Match",
                              backref = "tournament_player",
                              primaryjoin = "or_(TournamentPlayer.id==Match.tournament_player1_id, TournamentPlayer.id==Match.tournament_player2_id)",
                              lazy ='dynamic')

    forecasts = db.relationship("Forecast", backref = "winner", lazy = "dynamic")


    def get_full_name(self):
        full_name = u""
        if self.status:
            full_name += "[{}] ".format(self.status)
        if self.seed:
            full_name += "[{}] ".format(self.seed)
        if self.player:
            full_name += self.player.get_draw_name()
        else:
            full_name += u"Qualifié " + str(self.id)
        return full_name


class Match(db.Model):
    __tablename__ = "matches"
    id = db.Column(db.Integer, primary_key = True)
    created_at = db.Column(db.DateTime, default = datetime.datetime.now)
    deleted_at = db.Column(db.DateTime)

    position = db.Column(db.Integer)
    round = db.Column(db.Integer)
    score = db.Column(db.String(64))

    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'))

    forecasts = db.relationship("Forecast", backref = "match", lazy = "dynamic")

    winner_id = db.Column(db.Integer, db.ForeignKey('tournament_players.id'))
    winner = db.relationship("TournamentPlayer", foreign_keys = "Match.winner_id")
    tournament_player1_id = db.Column(db.Integer, db.ForeignKey('tournament_players.id'))
    tournament_player2_id = db.Column(db.Integer, db.ForeignKey('tournament_players.id'))
    tournament_player1 = db.relationship("TournamentPlayer", foreign_keys = "Match.tournament_player1_id")
    tournament_player2 = db.relationship("TournamentPlayer", foreign_keys = "Match.tournament_player2_id")

    def get_forecast(self, participant_id):
        forecast = (Forecast.query
                    .filter(Forecast.participant_id == participant_id)
                    .filter(Forecast.match_id == self.id)
                    .first()
                    )

        return forecast

    def get_next_match(self):
        if self.round == 1:
            return None
        else:
            match = (Match.query
                     .filter(Match.tournament_id == self.tournament_id)
                     .filter(Match.position == self.position // 2)
                     .first())
            return match


class Forecast(db.Model):
    __tablename__ = "forecasts"
    id = db.Column(db.Integer, primary_key = True)
    created_at = db.Column(db.DateTime, default = datetime.datetime.now)
    deleted_at = db.Column(db.DateTime, default = None)

    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'))
    winner_id = db.Column(db.Integer, db.ForeignKey('tournament_players.id'))
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'))
