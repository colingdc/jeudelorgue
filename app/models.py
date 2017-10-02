# -*- coding: utf-8 -*-

import datetime
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from . import db, bcrypt


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key = True)
    deleted = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, default = datetime.datetime.now)
    confirmed = db.Column(db.Boolean, default = False)
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

    def verify_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def generate_confirmation_token(self, expiration = 3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def generate_reset_token(self, expiration = 3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except :
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def get_id(self):
        return str(self.id)
