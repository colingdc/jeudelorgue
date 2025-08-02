# -*- coding: utf-8 -*-

import os
from datetime import timedelta
import babel

from flask import Flask, session, g, request, redirect, url_for
from flask_bcrypt import Bcrypt
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from flask_babel import Babel

from config import config
from instance import INSTANCE
from .lang import WORDINGS
from .utils import build_error_handler, display_info_toast

db = SQLAlchemy()
bcrypt = Bcrypt()
bootstrap = Bootstrap()
mail = Mail()
babel_ = Babel()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "danger"
login_manager.login_message = u"Veuillez vous connecter pour accéder à cette page."


def create_app(config_name=None):
    app = Flask(__name__)
    if config_name:
        app.config.from_object(config.get(config_name, "default"))
    else:
        app.config.from_object(config.get(INSTANCE, "default"))
    app.url_map.strict_slashes = False
    CSRFProtect(app)

    db.init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    babel_.init_app(app)

    def format_datetime(value):
        return babel.dates.format_datetime(value, "EEEE dd MMMM y 'à' HH:mm")

    app.jinja_env.filters['datetime'] = format_datetime

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.filter(User.id == int(user_id)).first()

    app.logger.addHandler(build_error_handler())

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

    return app
