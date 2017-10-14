# -*- coding: utf-8 -*-

from flask import render_template, abort
from . import main
from ..models import User


@main.route("/")
def landing():
    title = "Accueil"

    return render_template("main/homepage.html", title = title)


@main.route("/index")
def index():
    title = "Accueil"
    return render_template("main/index.html", title = title)


@main.route("/user/<username>")
def user(username):
    user = User.query.filter_by(username = username).first_or_404()
    title = "Profil de {}".format(username)
    return render_template("main/user.html", title = title, user = user)
