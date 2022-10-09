# -*- coding: utf-8 -*-

import os
from datetime import timedelta
import babel
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, session, g, request, redirect, url_for
from flask_bcrypt import Bcrypt
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from flask_babel import Babel

from config import config
from .lang import WORDINGS
from .utils import display_info_toast

db = SQLAlchemy()
bcrypt = Bcrypt()
bootstrap = Bootstrap()
mail = Mail()
babel_ = Babel()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "danger"
login_manager.login_message = u"Veuillez vous connecter pour accéder à cette page."


class PrefixMiddleware(object):

    def __init__(self, app, prefix=''):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):

        if environ['PATH_INFO'].startswith(self.prefix):
            environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
            environ['SCRIPT_NAME'] = self.prefix
            return self.app(environ, start_response)
        else:
            start_response('404', [('Content-Type', 'text/plain')])
            return ["This url does not belong to the app.".encode()]


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config.get(config_name, "default"))
    app.url_map.strict_slashes = False
    CSRFProtect(app)

    db.init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    babel_.init_app(app)

    def format_datetime(value, format='medium'):
        if format == 'long':
            format = "EEEE dd MMMM y 'à' HH:mm"
        elif format == 'medium':
            format = "dd MMMM y"
        elif format == 'short':
            format = "dd/MM/y"
        return babel.dates.format_datetime(value, format)

    app.jinja_env.filters['datetime'] = format_datetime

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.filter(User.id == int(user_id)).first()

    error_handler = RotatingFileHandler("logs/app.log", maxBytes=1000000, backupCount=1)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    error_handler.setFormatter(formatter)
    app.logger.addHandler(error_handler)

    @app.before_request
    def before_request():
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=60)
        session.modified = True
        g.user = current_user

        if (current_user.is_authenticated and
                not current_user.confirmed and
                current_user.is_old_account and
                request.endpoint[:5] != 'auth.' and
                not request.path.startswith('/static')):
            display_info_toast(WORDINGS.AUTH.OLD_ACCOUNT_PASSWORD_CHANGE)
            return redirect(url_for('auth.change_password'))

        if (current_user.is_authenticated and
                not current_user.confirmed and
                request.endpoint[:5] != 'auth.' and
                not request.path.startswith('/static')):
            return redirect(url_for('auth.unconfirmed'))

        rp = request.path
        if rp != '/' and rp.endswith('/'):
            return redirect(rp[:-1])

    @app.after_request
    def after_request(response):
        if response.status_code not in (403, 404, 500) and not request.full_path.startswith("/static"):
            app.logger.info(request.full_path)
        return response

    @app.template_filter('autoversion')
    def autoversion_filter(filename):
        # determining fullpath might be project specific
        fullpath = os.path.join('app/', filename[1:])
        try:
            timestamp = str(os.path.getmtime(fullpath))
        except OSError:
            return filename
        newfilename = "{0}?v={1}".format(filename, timestamp)
        return newfilename

    from .main import bp as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import bp as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .tournament import bp as tournament_blueprint
    app.register_blueprint(tournament_blueprint, url_prefix="/tournament")

    from .player import bp as player_blueprint
    app.register_blueprint(player_blueprint, url_prefix="/player")

    from .ranking import bp as ranking_blueprint
    app.register_blueprint(ranking_blueprint, url_prefix="/ranking")

    from .tournament_category import bp as tournament_category_blueprint
    app.register_blueprint(tournament_category_blueprint, url_prefix="/tournament_category")

    from .admin import bp as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix="/admin")

    # app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix = app.config.get("URL_PREFIX", "/jeudelorgue"))

    return app
