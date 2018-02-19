# -*- coding: utf-8 -*-

from flask_script import Manager, Shell, Command, Option
from flask_migrate import Migrate, MigrateCommand
from app import create_app, db
from app.models import *
from instance import INSTANCE
import pandas as pd
import os

COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch = True, include = "app/*")
    COV.start()


def make_shell_context():
    return dict(app = app,
                db = db,
                User = User,
                Role = Role,
                Permission = Permission,
                TournamentStatus = TournamentStatus,
                TournamentPlayer = TournamentPlayer,
                Tournament = Tournament,
                Match = Match,
                Player = Player,
                Forecast = Forecast,
                Participant = Participant,
                TournamentCategory = TournamentCategory)


app = create_app(INSTANCE)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command("db", MigrateCommand)
manager.add_command("shell", Shell(make_context = make_shell_context))


@manager.command
def test(coverage = False):
    """Run the unit tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover("tests")
    unittest.TextTestRunner(verbosity = 2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory = covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()


@manager.command
def import_accounts(filename):
    df = pd.read_csv(filename)
    df.fillna("", inplace = True)
    for i, row in df.iterrows():
        print("-" * 50)
        print("Importing user #{} : {}".format(i + 1, row["username"]))
        User.insert_user(email = row["email"],
                         username = row["username"],
                         password = row["password"],
                         role_name = "User",
                         confirmed = False,
                         is_old_account = True)


@manager.command
def import_tournaments(filename):
    df = pd.read_csv(filename)
    df.fillna("", inplace = True)
    for i, row in df.iterrows():
        print("-" * 50)
        print("Importing tournament #{} : {}".format(i + 1, row["name"]))
        Tournament.insert_tournament(name = row["name"],
                                     started_at = datetime.datetime.strptime(row["started_at"], "%Y-%m-%d"),
                                     ended_at = datetime.datetime.strptime(row["ended_at"], "%Y-%m-%d"),
                                     category_name = row["category"],
                                     old_website_id = row["id"])


@manager.command
def import_participants(filename):
    df = pd.read_csv(filename)
    df.fillna("", inplace = True)
    for i, row in df.iterrows():
        if row["filled"] and row["compte"]:
            user = User.query.filter_by(username = row["username"]).first()
            tournament = Tournament.query.filter_by(old_website_id = row["tournament_id"]).first()
            participant = Participant(user_id = user.id,
                                      old_website_id = row["id"],
                                      tournament_id = tournament.id,
                                      score = row["score"],
                                      risk_coefficient = row["risk_coefficient"],
                                      points = row["points"] + row["bonus"],
                                      ranking = row["ranking"])
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


if __name__ == "__main__":
    manager.run()
