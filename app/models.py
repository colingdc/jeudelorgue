# -*- coding: utf-8 -*-

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import datetime

db = SQLAlchemy()
bcrypt = Bcrypt()


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key = True)
    deleted = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, default = datetime.datetime.now)

    username = db.Column(db.String(64), index = True, unique = True)
    role = db.Column(db.String(120))
    email = db.Column(db.String(120), index = True, unique = True)
    password = db.Column(db.String(256), unique = False)

    def __repr__(self):
        return '<User %r>' % self.username

    def __init__(self, username, password, email, role = "USER"):
        self.username = username
        self.email = email
        self.password = bcrypt.generate_password_hash(password, rounds = 12)
        self.registered_on = datetime.datetime.now()
        self.role = role

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)
