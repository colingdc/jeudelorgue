# -*- coding: utf-8 -*-

from flask_script import Manager, Shell, Command, Option
from flask_migrate import Migrate, MigrateCommand
import os
import sys
import subprocess
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
        options = []

        for setting, klass in settings.items():
            if klass.cli:
                if klass.const is not None:
                    options.append(Option(*klass.cli, const=klass.const, action=klass.action))
                else:
                    options.append(Option(*klass.cli, action=klass.action))

        return options

    def run(self, *args, **kwargs):
        run_args = sys.argv[2:]
        # !!!!! Change your app here !!!!!
        run_args.append('--reload')
        run_args.append('manage:app')
        subprocess.Popen([os.path.join(os.path.dirname(sys.executable), 'gunicorn')] + run_args).wait()


manager.add_command("gunicorn", GunicornServer())


if __name__ == "__main__":
    manager.run()
