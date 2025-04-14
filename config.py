import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SSL_DISABLE = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SUBJECT_PREFIX = '[Jeu de L-orgue]'
    MAIL_SENDER = 'Le Jeu de L-orgue <jeudelorgue@gmail.com>'
    ADMIN_JDL = os.environ.get('ADMIN_JDL')
    TOURNAMENTS_PER_PAGE = 100
    PLAYERS_PER_PAGE = 100
    USERS_PER_PAGE = 100
    CATEGORIES_PER_PAGE = 100
    SLOW_DB_QUERY_TIME = 0.5
    BABEL_DEFAULT_LOCALE = "fr"
    WTF_CSRF_TIME_LIMIT = 3600 * 6
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    PRODUCTION = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL')
    URL_PREFIX = "/jeudelorgue/dev"


class TestingConfig(Config):
    TESTING = True
    PRODUCTION = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL')
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    PRODUCTION = True
    URL_PREFIX = "/jeudelorgue"

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # email errors to the administrators
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.MAIL_SENDER,
            toaddrs=[cls.ADMIN_JDL],
            subject=cls.MAIL_SUBJECT_PREFIX + ' Application Error',
            credentials=credentials,
            secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
