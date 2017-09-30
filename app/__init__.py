# -*- coding: utf-8 -*-

import logging
from datetime import timedelta
from logging.handlers import RotatingFileHandler

from flask import Flask, session, g, request
from flask_bcrypt import Bcrypt
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

from config import config

db = SQLAlchemy()
bcrypt = Bcrypt()
bootstrap = Bootstrap()
mail = Mail()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "danger"


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config.get(config_name, "default"))

    db.init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.filter(User.id == int(user_id)).first()

    error_handler = RotatingFileHandler("logs/app.log", maxBytes = 1000000, backupCount = 1)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    error_handler.setFormatter(formatter)
    app.logger.addHandler(error_handler)

    @app.before_request
    def before_request():
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes = 60)
        session.modified = True
        g.user = current_user

    @app.after_request
    def after_request(response):
        if response.status_code not in (403, 404, 500) and not request.full_path.startswith("/static"):
            app.logger.info(request.full_path)
        return response

    from .main import main as main_blueprint
    from .auth import auth as auth_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)

    return app
