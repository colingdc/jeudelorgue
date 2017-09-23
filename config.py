# -*- coding: utf-8 -*-

import os

basedir = os.path.abspath(os.path.dirname(__file__))
username = os.environ['APP_USERNAME']
password = os.environ['APP_PASSWORD']
credentials = dict(username = username, password = password)

WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'
SQLALCHEMY_DATABASE_URI = "mysql://{username}:{password}@localhost/jeudelorgue".format(**credentials)
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = True
