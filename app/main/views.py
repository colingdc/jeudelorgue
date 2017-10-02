# -*- coding: utf-8 -*-

from flask import render_template
from . import main


@main.route("/")
def landing():
    title = "Accueil"

    return render_template("main/homepage.html", title = title)



@main.route("/index")
def index():
    title = "Accueil"
    return render_template("main/index.html", title = title)
