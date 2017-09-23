# -*- coding: utf-8 -*-

from flask import render_template, redirect
from app import app
from .forms import LoginForm


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html",
                           title = "Accueil")


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect("/index")

    return render_template('login.html',
                           title = "Connexion",
                           form = form)
