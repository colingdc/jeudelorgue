# -*- coding: utf-8 -*-

from flask import render_template, redirect, request, flash, url_for

from . import admin
from .forms import CreateTournamentForm
from .. import db
from ..models import Tournament
from ..decorators import manager_required


@admin.route("/tournament/create", methods = ["GET", "POST"])
@manager_required
def create_tournament():
    form = CreateTournamentForm(request.form)

    if form.validate_on_submit():

        tournament = Tournament(name = form.name.data,
                                started_at = form.start_date.data,
                                number_rounds = form.number_rounds.data)
        db.session.add(tournament)
        db.session.commit()
        flash("Le tournoi {} a été créé".format(form.name.data), "info")
        return redirect(url_for(".create_tournament"))
    else:
        return render_template("admin/create_tournament.html", form = form)
