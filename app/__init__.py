# -*- coding: utf-8 -*-

from flask import Flask, session, g, render_template, request
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, current_user
import logging
from logging.handlers import RotatingFileHandler
from datetime import timedelta


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    from .models import db, User
    db.init_app(app)

    Bootstrap(app)
    login_manager = LoginManager(app)

    login_manager.login_view = "login"
    login_manager.login_message_category = "danger"

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

    @app.errorhandler(403)
    def forbidden_page(error):
        app.logger.error(error)
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def page_not_found(error):
        app.logger.error(error)
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error_page(error):
        app.logger.error(error)
        return render_template("errors/500.html"), 500

    from .views import bp as main_blueprint

    app.register_blueprint(main_blueprint)

    return app
