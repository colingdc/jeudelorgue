# -*- coding: utf-8 -*-

import os
import time
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

from app import create_app
from app.models import *
from instance import INSTANCE
import pandas as pd

COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage

    COV = coverage.coverage(branch=True, include="app/*")
    COV.start()


def make_shell_context():
    return dict(
        app=app,
        db=db,
        User=User,
        Role=Role,
        Permission=Permission,
        TournamentStatus=TournamentStatus,
        TournamentPlayer=TournamentPlayer,
        Tournament=Tournament,
        Match=Match,
        Player=Player,
        Forecast=Forecast,
        Participant=Participant,
        TournamentCategory=TournamentCategory,
        Ranking=Ranking
    )


app = create_app(INSTANCE)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command("db", MigrateCommand)
manager.add_command("shell", Shell(make_context=make_shell_context))


@manager.command
def test(coverage=False):
    """Run the unit tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover("tests")
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()


@manager.command
def import_players(filename):
    df = pd.read_csv(filename)
    df.fillna("", inplace=True)
    for i, row in df.iterrows():
        if Player.query.filter(Player.first_name == row["first_name"]).filter(
                Player.last_name == row["last_name"]).first() is None:
            player = Player(
                first_name=row["first_name"],
                last_name=row["last_name"]
            )
            db.session.add(player)
            print("-" * 50)
            print(row["last_name"])
    db.session.commit()


@manager.command
def import_accounts(filename):
    df = pd.read_csv(filename)
    df.fillna("", inplace=True)
    for i, row in df.iterrows():
        print("-" * 50)
        print("Importing user #{} : {}".format(i + 1, row["username"]))
        User.insert_user(
            email=row["email"],
            username=row["username"],
            password=row["password"],
            role_name="User",
            confirmed=False,
            is_old_account=True
        )


@manager.command
def import_tournaments(filename):
    df = pd.read_csv(filename)
    df.fillna("", inplace=True)
    for i, row in df.iterrows():
        print("-" * 50)
        print("Importing tournament #{} : {}".format(i + 1, row["name"]))
        Tournament.insert_tournament(
            name=row["name"],
            started_at=datetime.datetime.strptime(row["started_at"], "%Y-%m-%d"),
            ended_at=datetime.datetime.strptime(row["ended_at"], "%Y-%m-%d"),
            category_name=row["category"],
            old_website_id=row["id"]
        )
        time.sleep(1)


@manager.command
def import_participants(filename):
    df = pd.read_csv(filename)
    df.fillna("", inplace=True)
    for i, row in df.iterrows():
        if row["filled"] and row["compte"]:
            user = User.query.filter_by(username=row["username"]).first()
            tournament = Tournament.query.filter_by(old_website_id=row["tournament_id"]).first()
            participant = Participant(
                user_id=user.id,
                old_website_id=row["id"],
                tournament_id=tournament.id,
                score=row["score"],
                risk_coefficient=row["risk_coefficient"],
                points=row["points"] + row["bonus"],
                ranking=row["ranking"]
            )
            db.session.add(participant)
            print(tournament.name, user.username)
    db.session.commit()


@manager.command
def compute_all_rankings():
    for user in User.query.all():
        user.annual_points = user.get_annual_points()
        user.year_to_date_points = user.get_year_to_date_points()
        db.session.add(user)
        print(user.username)
    db.session.commit()


@manager.command
def import_tournament_draws(filename, tournament_id):
    bye = Player.query.filter(Player.last_name == "Bye").filter(Player.deleted_at.is_(None)).first()
    df = pd.read_csv(filename)
    df = df.dropna(subset=["player_name"])
    df.fillna("", inplace=True)

    df = df[df["username"] == ""]
    df = df[df["tournament_id"] == int(tournament_id)]

    for i, group in df.groupby("tournament_id"):
        print("-" * 50)
        print("Tournament #", i)
        tournament = Tournament.query.filter(Tournament.old_website_id == i).first()
        print(tournament.name)

        # for pos in range(1, 2 ** tournament.number_rounds):
        #     match = Match(position = pos,
        #                   tournament_id = tournament.id,
        #                   round = floor(log(pos) / log(2)) + 1)
        #     db.session.add(match)
        # db.session.commit()

        for match_id, row in group.iterrows():
            r = row["round"]

            position = 2 ** (tournament.number_rounds - r) + (row["position"] - 1) // 2

            if "bye" in row["player_name"].lower():
                player = bye
                player_id = player.id
            elif Player.get_closest_player(row["player_name"]):
                player = Player.get_closest_player(row["player_name"])
                player_id = player.id
            else:
                player = None
                player_id = None

            seed = Player.get_seed(row["player_name"])
            status = Player.get_status(row["player_name"])

            if r == 1:
                pass
                t = TournamentPlayer(
                    player_id=player_id,
                    seed=seed,
                    status=status,
                    position=(1 + row["position"]) % 2,
                    tournament_id=tournament.id
                )
                # Add tournament player
                db.session.add(t)
                db.session.commit()

                match = Match.query.filter(Match.position == position).filter(
                    Match.tournament_id == tournament.id).first()

                if row["position"] % 2 == 1:
                    match.tournament_player1_id = t.id
                else:
                    match.tournament_player2_id = t.id

                db.session.add(match)
                db.session.commit()

            elif r <= tournament.number_rounds:
                match = Match.query.filter(Match.position == position).filter(
                    Match.tournament_id == tournament.id).first()
                t = TournamentPlayer.query.filter(TournamentPlayer.tournament_id == tournament.id).filter(
                    TournamentPlayer.player_id == player_id).first()

                if row["position"] % 2 == 1:
                    match.tournament_player1_id = t.id
                else:
                    match.tournament_player2_id = t.id

                for i_previous, previous_match in enumerate(match.get_previous_matches()):
                    if row["position"] % 2 == 1 - i_previous:
                        previous_match.winner_id = t.id
                db.session.add(match)
                db.session.add(previous_match)
                db.session.commit()

            else:
                match = Match.query.filter(Match.position == 1).filter(Match.tournament_id == tournament.id).first()
                t = TournamentPlayer.query.filter(TournamentPlayer.tournament_id == tournament.id).filter(
                    TournamentPlayer.player_id == player_id).first()
                match.winner_id = t.id
                db.session.add(match)
                db.session.commit()


@manager.command
def import_participant_draws(filename, tournament_id):
    df = pd.read_csv(filename)

    df = df.dropna(subset=["username"])
    df.fillna("", inplace=True)

    df = df[df["tournament_id"] == int(tournament_id)]

    for (tournament_id, username), group in df.groupby(["tournament_id", "username"]):
        tournament = Tournament.query.filter(Tournament.old_website_id == tournament_id).first()
        print(tournament.name, username)
        participant = (Participant.query.filter(Participant.tournament_id == tournament.id)
                       .join(User, User.id == Participant.user_id)
                       .filter(User.username == username)).first()
        if participant is None:
            print(username, "not recognized")
            continue

        for match_id, row in group.iterrows():
            r = row["round"]

            position = 2 ** (tournament.number_rounds - r + 1) + (row["position"] - 1)

            player = Player.get_closest_player(row["player_name"])
            tournament_player_id = None
            if player:
                tournament_player = TournamentPlayer.query.filter(
                    TournamentPlayer.tournament_id == tournament.id).filter(
                    TournamentPlayer.player_id == player.id).first()
                if tournament_player:
                    tournament_player_id = tournament_player.id

            if r <= tournament.number_rounds:
                match = Match.query.filter(Match.position == position).filter(
                    Match.tournament_id == tournament.id).first()

                forecast = Forecast(
                    match_id=match.id,
                    winner_id=tournament_player_id,
                    participant_id=participant.id)

                db.session.add(forecast)

            else:
                match = Match.query.filter(Match.position == 1).filter(Match.tournament_id == tournament.id).first()
                forecast = Forecast(
                    match_id=match.id,
                    winner_id=tournament_player_id,
                    participant_id=participant.id
                )

                db.session.add(forecast)

        db.session.commit()


@manager.command
def import_surfaces(filename):
    df = pd.read_csv(filename)

    for i, row in df.iterrows():
        tournament = Tournament.query.filter(Tournament.name == row["name"]).first()
        surface = Surface.query.filter(Surface.name == row["surface"]).first()

        tournament.surface_id = surface.id
        db.session.add(surface)
        print(tournament.id, surface.name)
    db.session.commit()


@manager.command
def close_registrations(tournament_id):
    tournament = Tournament.query.get(tournament_id)
    tournament.status = TournamentStatus.ONGOING
    db.session.add(tournament)
    db.session.commit()

    for participant in tournament.participants:
        if not participant.has_filled_draw():
            db.session.delete(participant)
    db.session.commit()

    for participant in tournament.participants:
        participant.risk_coefficient = participant.get_risk_coefficient()
        db.session.add(participant)
    db.session.commit()


if __name__ == "__main__":
    manager.run()
