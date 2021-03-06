# -*- coding: utf-8 -*-

import datetime
from dateutil.relativedelta import relativedelta
from math import log, exp, floor
import pandas as pd
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
    is_old_account = db.Column(db.Boolean, default = False)
    username = db.Column(db.String(64), index = True, unique = True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    email = db.Column(db.String(120), index = True)
    password_hash = db.Column(db.String(128))
    annual_points = db.Column(db.Integer)
    year_to_date_points = db.Column(db.Integer)

    participants = db.relationship("Participant", backref = "user", lazy = "dynamic")
    rankings = db.relationship("Ranking", backref = "user", lazy = "dynamic")


    def __repr__(self):
        return "<User %r>" % self.username

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        if self.role is None:
            if self.email == current_app.config['ADMIN_JDL']:
                self.role = Role.query.filter_by(permissions = 0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default = True).first()


    def is_anonymous(self):
        return False

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
    def insert_user(email, role_name = "User", username = None, confirmed = True, password = "test1234", is_old_account = False):
        role = Role.query.filter_by(name = role_name).first()
        if role is None:
            print("This role does not exist")
        else:
            if username is None:
                username = email
            user = User(email = email,
                        role = role,
                        confirmed = confirmed,
                        is_old_account = is_old_account,
                        username = username,
                        password = password)
            try:
                db.session.add(user)
                db.session.commit()
                print("Import successful")
            except Exception as e:
                print("\n")
                print(str(e))
                db.session.rollback()


    def get_id(self):
        return str(self.id)

    def get_participant(self, tournament_id):
        return (Participant.query
                .filter(Participant.tournament_id == tournament_id)
                .filter(Participant.user_id == self.id)
                .filter(Participant.deleted_at.is_(None))
                ).first()

    def is_registered_to_tournament(self, tournament_id):
        return self.get_participant(tournament_id) is not None

    @property
    def all_participations(self):
        participations = (self.participants
                          .join(Tournament, Tournament.id == Participant.tournament_id)
                          .filter(Tournament.deleted_at.is_(None))
                          .filter(Tournament.status == TournamentStatus.FINISHED))
        return participations

    @property
    def year_to_date_participations(self):
        participations = (self.all_participations
                          .filter(func.year(Tournament.started_at) == datetime.datetime.now().year)
                          .filter(Tournament.started_at <= datetime.datetime.now()))
        return participations

    @property
    def annual_participations(self):
        participations = (self.all_participations
                          .filter(Tournament.started_at >= datetime.datetime.now() - relativedelta(years = 1))
                          .filter(Tournament.started_at <= datetime.datetime.now()))
        return participations

    def get_annual_points(self):
        points = sum(participation.points for participation in self.annual_participations if participation.points is not None)
        if not points:
            points = 0
        return points

    def get_year_to_date_points(self):
        points = sum(participation.points for participation in self.year_to_date_participations if participation.points is not None) or 0
        if not points:
            points = 0
        return points

    def participants_sorted(self):
        return (self.participants.order_by(Participant.created_at.desc()))

    def get_titles(self):
        return self.participants.join(Tournament, Tournament.id == Participant.tournament_id).filter(Tournament.deleted_at.is_(None)).filter(Tournament.status == TournamentStatus.FINISHED).filter(Participant.ranking == 1)

    def get_best_tournament_rank(self):
        return self.participants.join(Tournament, Tournament.id == Participant.tournament_id).filter(Tournament.deleted_at.is_(None)).filter(Tournament.status == TournamentStatus.FINISHED).order_by(Participant.ranking).first()

    def get_current_ranking(self):
        latest_tournament = Tournament.get_latest_finished_tournament()
        return Ranking.query.filter(Ranking.user_id == self.id).filter(Ranking.tournament_id == latest_tournament.id).first()


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

    def is_manager(self):
        return False

    def is_anonymous(self):
        return True


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
        return self.name


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

    old_website_id = db.Column(db.Integer, default = None)
    name = db.Column(db.String(64))
    tournament_topic_url = db.Column(db.String(64))
    jeudelorgue_topic_url = db.Column(db.String(64))
    name = db.Column(db.String(64))
    started_at = db.Column(db.DateTime)
    ended_at = db.Column(db.DateTime, default = None)
    status = db.Column(db.Integer, default = TournamentStatus.CREATED)
    maximal_score = db.Column(db.Integer)
    current_maximal_score = db.Column(db.Integer, default = 0)

    category_id = db.Column(db.Integer, db.ForeignKey("tournament_categories.id"))
    category = db.relationship("TournamentCategory", foreign_keys = category_id)
    surface_id = db.Column(db.Integer, db.ForeignKey("surfaces.id"))
    surface = db.relationship("Surface", foreign_keys = surface_id)

    matches = db.relationship("Match", backref = "tournament", lazy = "dynamic")
    participants = db.relationship("Participant", backref = "tournament", lazy = "dynamic")
    players = db.relationship("TournamentPlayer", backref = "tournament", lazy = "dynamic")
    rankings = db.relationship("Ranking", backref = "tournament", lazy = "dynamic")

    def is_created(self):
        return self.status == TournamentStatus.CREATED

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

    def get_matches_first_round_last16(self):
        return [m for m in self.matches if m.round == 4]

    def get_matches_by_round(self):
        return [{"round": i,
                 "matches": self.matches.filter(Match.round == i).all(),
                 "first_round": i == self.number_rounds}
                for i in range(self.number_rounds, 0, -1)]

    def get_matches_by_round_last_rounds(self, rounds):
        return [rd for rd in self.get_matches_by_round() if rd["round"] <= rounds]

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

    def get_round_names_last16(self):
        names = ["F", "DF", "QF", "HF"]
        return names[::-1]


    def get_score_per_round(self):
        if self.number_rounds < 7:
            return {round: 2 ** (self.number_rounds - round)
                    for round in range(1, self.number_rounds + 1)}
        return {round: 2 ** (self.number_rounds - round - 1) if round < self.number_rounds else 1
                for round in range(1, self.number_rounds + 1)}

    def get_risk_coefficient_per_round(self):
        return {round: 2 ** (self.number_rounds - round)
                    for round in range(1, self.number_rounds + 1)}

    def get_maximal_score(self):
        score_per_round = self.get_score_per_round()
        score = 0
        for match in self.matches:
            if match.tournament_player1 and match.tournament_player1.player and match.tournament_player1.player.last_name == "Bye":
                continue
            if match.tournament_player2 and match.tournament_player2.player and match.tournament_player2.player.last_name == "Bye":
                continue
            match_score = score_per_round[match.round]
            score += match_score
        return score


    def get_current_maximal_score(self):
        score_per_round = self.get_score_per_round()
        score = 0
        for match in self.matches:
            if match.tournament_player1 and match.tournament_player1.player and match.tournament_player1.player.last_name == "Bye":
                continue
            if match.tournament_player2 and match.tournament_player2.player and match.tournament_player2.player.last_name == "Bye":
                continue
            if match.winner_id:
                match_score = score_per_round[match.round]
                score += match_score
        return score


    def get_current_maximal_score_simulator(self, scenario):
        score_per_round = self.get_score_per_round()
        score = 0
        for match in self.matches:
            if match.tournament_player1 and match.tournament_player1.player and match.tournament_player1.player.last_name == "Bye":
                continue
            if match.tournament_player2 and match.tournament_player2.player and match.tournament_player2.player.last_name == "Bye":
                continue
            if scenario.get(match.id):
                match_score = score_per_round[match.round]
                score += match_score
        return score

    def participants_sorted(self):
        return (self.participants.order_by(Participant.score.desc(), Participant.risk_coefficient.desc(), Participant.created_at))

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
        participants = self.participants.order_by(Participant.score.desc(), Participant.risk_coefficient.desc(), Participant.created_at)
        number_participants = participants.count()
        if number_participants == 1:
            return {participants.first(): self.category.maximal_score}

        def ranking_score(rank):
            return self.category.minimal_score * (0.9 * self.category.maximal_score / self.category.minimal_score) ** ((number_participants - rank - 1.) / (number_participants - 1.))

        maximal_score = participants.first().score
        minimal_score = participants.all()[-1].score

        def score_score(score):
            return 0.1 * self.category.maximal_score * (score - minimal_score) / (maximal_score - minimal_score)

        scores = {participant: round(ranking_score(rank) + score_score(participant.score)) for rank, participant in enumerate(participants)}
        return scores

    @classmethod
    def get_current_tournament(cls):
        return cls.query.filter(cls.status < TournamentStatus.FINISHED).order_by(cls.started_at.desc()).first()

    @classmethod
    def get_recent_tournaments(cls, number_tournaments):
        return cls.query.order_by(cls.started_at.desc()).filter(cls.deleted_at.is_(None)).limit(number_tournaments)

    @classmethod
    def get_latest_finished_tournament(cls):
        return cls.query.filter(cls.status == TournamentStatus.FINISHED).order_by(cls.started_at.desc()).first()

    @staticmethod
    def insert_tournament(name, started_at, ended_at, category_name, old_website_id = None, status = TournamentStatus.FINISHED):
        category = TournamentCategory.query.filter_by(name = category_name).first()
        if category is None:
            print("This category does not exist")
        else:
            tournament = Tournament(name = name,
                                    old_website_id = old_website_id,
                                    started_at = started_at,
                                    ended_at = ended_at,
                                    category = category,
                                    status = status)
            try:
                db.session.add(tournament)
                db.session.commit()
                print("Import successful")
            except Exception as e:
                print("\n")
                print(str(e))
                db.session.rollback()
    @property
    def players_alphabetic(self):
        return self.players.join(Player, Player.id == TournamentPlayer.player_id).order_by(Player.last_name, Player.first_name)


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


class Surface(db.Model):
    __tablename__ = "surfaces"
    id = db.Column(db.Integer, primary_key = True)
    created_at = db.Column(db.DateTime, default = datetime.datetime.now)
    deleted_at = db.Column(db.DateTime, default = None)

    name = db.Column(db.String(64))
    class_name = db.Column(db.String(64))

    @classmethod
    def get_all_surfaces(cls):
        return [(p.id, p.name) for p in cls.query.order_by(cls.name).all()]


    @staticmethod
    def insert_surfaces():
        surfaces = [("Dur", "surface-hard"),
                    ("Gazon", "surface-grass"),
                    ("Terre battue", "surface-clay")]
        for (s, c) in surfaces:
            surface = Surface(name = s,
                              class_name = c)
            db.session.add(surface)
        db.session.commit()


class Participant(db.Model):
    __tablename__ = "participants"
    id = db.Column(db.Integer, primary_key = True)
    created_at = db.Column(db.DateTime, default = datetime.datetime.now)
    deleted_at = db.Column(db.DateTime, default = None)
    matches_not_forecasted = db.Column(db.Integer, default = None)
    score = db.Column(db.Integer, default = 0)
    risk_coefficient = db.Column(db.Float, default = 0)
    points = db.Column(db.Integer, default = 0)
    ranking = db.Column(db.Integer, default = None)

    old_website_id = db.Column(db.Integer, default = None)

    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    forecasts = db.relationship("Forecast", backref = "participant", lazy = "dynamic")

    def has_filled_draw(self):
        return len(self.forecasts.all()) > 0

    def has_completely_filled_draw(self):
        return self.has_filled_draw() and len(self.forecasts.filter(Forecast.winner_id).all()) == len(self.forecasts.all())

    def get_score(self):
        score_per_round = self.tournament.get_score_per_round()
        number_byes = sum(1 for p in self.tournament.players if p.player and p.player.last_name == "Bye")

        matches = {m.id: (m.winner_id, m.round) for m in Match.query.filter(Match.tournament_id == self.tournament.id)}
        forecasts = {f.match_id: f.winner_id for f in self.forecasts if f.winner_id}

        score = sum((matches[match_id][0] == winner_id) * score_per_round[matches[match_id][1]] for match_id, winner_id in forecasts.items())

        return score - number_byes


    def get_score_simulator(self, scenario):
        """
        scenario : dict containing hypothetical match results
        (match_id: winner_id)
        """
        score_per_round = self.tournament.get_score_per_round()
        score = 0

        for forecast in self.forecasts:
            result = forecast.match
            if result.tournament_player1 and result.tournament_player1.player and result.tournament_player1.player.last_name == "Bye":
                continue
            if result.tournament_player2 and result.tournament_player2.player and result.tournament_player2.player.last_name == "Bye":
                continue
            match_score = (scenario[forecast.match.id] == forecast.winner_id) * score_per_round[result.round]
            score += match_score
        return score

    def get_risk_coefficient(self):
        if self.tournament.participants.count() < 2:
            return 0

        score_per_round = self.tournament.get_risk_coefficient_per_round()

        query = (db.session.query(Forecast.winner_id.label("participant_winner_id"),
                                  Forecast.match_id)
                        .join(Match, Match.id == Forecast.match_id)
                        .filter(Match.tournament_id == self.tournament.id)
                        .filter(Forecast.participant_id == self.id)
                        )

        participant_forecasts = pd.read_sql(query.statement, query.session.bind)

        query = (db.session.query(Forecast.participant_id,
                                 Forecast.winner_id,
                                 Forecast.match_id,
                                 Match.round)
                        .join(Match, Match.id == Forecast.match_id)
                        .filter(Match.tournament_id == self.tournament.id)
                        .filter(Forecast.participant_id != self.id)
                        )

        other_forecasts = pd.read_sql(query.statement, query.session.bind)
        other_forecasts["match_score"] = other_forecasts["round"].apply(lambda x: score_per_round[x])

        merged = other_forecasts.merge(participant_forecasts, on = "match_id", how = "left")
        weighted_divergent_forecasts = sum(merged[merged["winner_id"] != merged["participant_winner_id"]]["match_score"])
        return weighted_divergent_forecasts / self.tournament.participants.count()

    def get_old_website_draw_url(self):
        return "http://www.jeudelorgue.raidghost.com/voir.php?tournoi={}&participant={}".format(self.tournament.old_website_id, self.old_website_id)


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

    @classmethod
    def get_closest_player(cls, player_name):
        if "[" in player_name:
            player_name = player_name[:player_name.find("[")] + player_name[1 + player_name.find("]"):]
            player_name = player_name.strip()
        last_name = player_name.split(". ")[-1].lower().replace("-", " ")
        first_name_initial = player_name.split(". ")[0]
        closest_player = cls.query.filter(func.lower(cls.last_name) == last_name).filter(cls.first_name.like(first_name_initial + "%")).first()
        return closest_player

    @staticmethod
    def get_seed(player_name):
        if "[" in player_name:
            between_brackets = player_name[1 + player_name.find("["): player_name.find("]")]
            try:
                seed = int(between_brackets)
                return seed
            except ValueError:
                return None
        return None

    @staticmethod
    def get_status(player_name):
        if "[" in player_name:
            between_brackets = player_name[1 + player_name.find("["): player_name.find("]")]
            try:
                seed = int(between_brackets)
                return None
            except ValueError:
                return between_brackets
        return None


class TournamentPlayer(db.Model):
    __tablename__ = "tournament_players"
    id = db.Column(db.Integer, primary_key = True)
    created_at = db.Column(db.DateTime, default = datetime.datetime.now)
    deleted_at = db.Column(db.DateTime, default = None)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'))

    seed = db.Column(db.Integer)
    status = db.Column(db.String(8))
    qualifier_id = db.Column(db.Integer)

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
            full_name += u"Qualifié " + str(self.qualifier_id)
        return full_name

    def get_full_name_surname_first(self):
        if self.player:
            return u"{}, {}".format(self.player.last_name.upper(), self.player.first_name)
        else:
            return u"Qualifié " + str(self.qualifier_id)

    def is_eliminated(self):
        matches = (Match.query
                   .filter(or_(Match.tournament_player1_id == self.id,
                                         Match.tournament_player2_id == self.id))
                   .filter(Match.winner_id.isnot(None))
                   .filter(Match.winner_id != self.id)
                   )
        return matches.count() > 0

    def is_bye(self):
        return self.player and self.player.last_name == "Bye"


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
        match = (Match.query
                 .filter(Match.tournament_id == self.tournament_id)
                 .filter(Match.position == self.position // 2)
                 .first())
        return match

    def get_previous_match(self, position):
        if self.round == self.tournament.number_rounds:
            return None
        match = (Match.query
                 .filter(Match.tournament_id == self.tournament_id)
                 .filter(Match.position == 2 * self.position + position)
                 .first())
        return match

    def get_previous_matches(self):
        if self.round == self.tournament.number_rounds:
            return None
        matches = (Match.query
                 .filter(Match.tournament_id == self.tournament_id)
                 .filter(or_(Match.position == 2 * self.position, Match.position == 2 * self.position + 1))
                 .all())
        return matches

    def has_bye(self):
        if self.round < self.tournament.number_rounds:
            return False
        return ((self.tournament_player1 and self.tournament_player1.player and self.tournament_player1.player.last_name == "Bye")
            or (self.tournament_player2 and self.tournament_player2.player and self.tournament_player2.player.last_name == "Bye"))


class Forecast(db.Model):
    __tablename__ = "forecasts"
    id = db.Column(db.Integer, primary_key = True)
    created_at = db.Column(db.DateTime, default = datetime.datetime.now)
    deleted_at = db.Column(db.DateTime, default = None)

    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'))
    winner_id = db.Column(db.Integer, db.ForeignKey('tournament_players.id'))
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'))


class Ranking(db.Model):
    __tablename__ = "rankings"
    id = db.Column(db.Integer, primary_key = True)
    created_at = db.Column(db.DateTime, default = datetime.datetime.now)
    deleted_at = db.Column(db.DateTime)

    annual_points = db.Column(db.Integer)
    annual_ranking = db.Column(db.Integer)
    annual_number_tournaments = db.Column(db.Integer)

    year_to_date_points = db.Column(db.Integer)
    year_to_date_ranking = db.Column(db.Integer)
    year_to_date_number_tournaments = db.Column(db.Integer)

    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @staticmethod
    def compute_historical_rankings(tournament = None):
        participations = (Participant.query
                          .join(Tournament, Tournament.id == Participant.tournament_id)
                          .filter(Tournament.deleted_at.is_(None))
                          .filter(Tournament.status == TournamentStatus.FINISHED)
                          )

        if tournament is None:
            tournament = Tournament.query.order_by(Tournament.started_at.desc()).first()

        participations = participations.filter(Tournament.started_at <= tournament.started_at)
        participations = participations.with_entities(Participant.user_id, Participant.points, Tournament.started_at)

        df = pd.read_sql(participations.statement, participations.session.bind)
        df["number_tournaments"] = 1
        df = df.dropna()

        annual_points = df[df["started_at"] > tournament.started_at - relativedelta(years = 1)].groupby("user_id").sum().sort_values("points", ascending = False).reset_index()
        annual_points["rank"] = range(1, len(annual_points) + 1)
        year_to_date_points = df[df["started_at"].dt.year == tournament.started_at.year].groupby("user_id").sum().sort_values("points", ascending = False).reset_index()
        year_to_date_points["rank"] = range(1, len(year_to_date_points) + 1)

        print("Computing annual points and rankings")
        for _, row in annual_points.iterrows():
            r = Ranking.query.filter(Ranking.tournament_id == tournament.id).filter(Ranking.user_id == row["user_id"]).first()
            if r is None:
                r = Ranking(user_id = row["user_id"], tournament_id = tournament.id)
            r.annual_points = row["points"]
            r.annual_ranking = row["rank"]
            r.annual_number_tournaments = row["number_tournaments"]
            db.session.add(r)

        print("Computing year to date points and rankings")
        for _, row in year_to_date_points.iterrows():
            r = Ranking.query.filter(Ranking.tournament_id == tournament.id).filter(Ranking.user_id == row["user_id"]).first()
            if r is None:
                r = Ranking(user_id = row["user_id"], tournament_id = tournament.id)
            r.year_to_date_points = row["points"]
            r.year_to_date_ranking = row["rank"]
            r.year_to_date_number_tournaments = row["number_tournaments"]
            db.session.add(r)

        db.session.commit()

    @staticmethod
    def get_historical_annual_ranking(tournament_id):
        return (User.query
                .join(Ranking, Ranking.user_id == User.id)
                .filter(Ranking.tournament_id == tournament_id)
                .filter(Ranking.annual_ranking.isnot(None))
                .order_by(Ranking.annual_ranking)
                .with_entities(User.id, User.username, Ranking.annual_number_tournaments, Ranking.annual_points, Ranking.annual_ranking)
                )

    @staticmethod
    def get_historical_race_ranking(tournament_id):
        return (User.query
                .join(Ranking, Ranking.user_id == User.id)
                .filter(Ranking.tournament_id == tournament_id)
                .filter(Ranking.year_to_date_ranking.isnot(None))
                .with_entities(User.id, User.username, Ranking.year_to_date_number_tournaments, Ranking.year_to_date_points, Ranking.year_to_date_ranking)
                .order_by(Ranking.year_to_date_ranking))

    @classmethod
    def generate_chart(cls, user_id):
        return (Tournament.query
                .outerjoin(cls, cls.tournament_id == Tournament.id)
                .filter(cls.user_id == user_id)
                .order_by(Tournament.started_at)
                .with_entities(Tournament.id, Tournament.name, Tournament.started_at,
                               Ranking.annual_ranking, Ranking.year_to_date_ranking)
                )
