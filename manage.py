# -*- coding: utf-8 -*-

import os
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

from app import create_app
from app.models import *
from instance import INSTANCE

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
