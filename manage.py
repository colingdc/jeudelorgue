# -*- coding: utf-8 -*-

from flask_script import Manager, Shell, Command, Option
from flask_migrate import Migrate, MigrateCommand
import os
from app import create_app, db
from app.models import *

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


app = create_app(os.getenv("FLASK_CONFIG") or "default")
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


class GunicornServer(Command):
    """Run the app within Gunicorn"""

    def get_options(self):
        from gunicorn.config import make_settings

        settings = make_settings()
        options = (
            Option(*klass.cli, action=klass.action)
            for setting, klass in settings.items() if klass.cli
        )
        return options

    def run(self, *args, **kwargs):
        from gunicorn.app.wsgiapp import WSGIApplication

        app = WSGIApplication()
        app.app_uri = 'manage:app'
        return app.run()


manager.add_command("gunicorn", GunicornServer())


if __name__ == "__main__":
    manager.run()
