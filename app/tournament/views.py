# -*- coding: utf-8 -*-

from flask import render_template, redirect, request, flash, url_for, current_app, abort
from flask_login import login_required, current_user
import datetime
from math import log, floor

from . import bp
from .forms import CreateTournamentForm, EditTournamentForm, CreateTournamentDrawForm, PlayerTournamentDrawForm, FillTournamentDrawForm
from .. import db
from ..decorators import manager_required
from ..models import Tournament, TournamentStatus, Participant, Match, TournamentPlayer, Player
from ..texts import (REGISTRATION_CLOSED, REGISTRATION_OPENED, REGISTERED_TO_TOURNAMENT, REGISTRATION_NOT_OPEN,
                     ALREADY_REGISTERED)


@bp.route("/create", methods = ["GET", "POST"])
@manager_required
def create_tournament():
    title = u"Créer un tournoi"
    form = CreateTournamentForm(request.form)
    if form.validate_on_submit():
        tournament = Tournament(name = form.name.data,
                                started_at = form.start_date.data,
                                number_rounds = form.number_rounds.data)
        db.session.add(tournament)
        db.session.commit()
        for i in range(1, 2 ** form.number_rounds.data):
            match = Match(position = i,
                          tournament_id = tournament.id,
                          round = floor(log(i) / log(2)) + 1)
            db.session.add(match)
        db.session.commit()
        flash("Le tournoi {} a été créé".format(form.name.data), "info")
        return redirect(url_for(".view_tournament", tournament_id = tournament.id))
    else:
        return render_template("tournament/create_tournament.html", title = title,
                               form = form)


@bp.route("/<tournament_id>/edit", methods = ["GET", "POST"])
@manager_required
def edit_tournament(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    title = u"Tournoi {}".format(tournament.name)
    form = EditTournamentForm(request.form)
    if request.method == "GET":
        form.name.data = tournament.name
        form.number_rounds.data = tournament.number_rounds
        form.start_date.data = tournament.started_at
    if form.validate_on_submit():
        tournament.name = form.name.data
        tournament.started_at = form.start_date.data
        db.session.add(tournament)
        db.session.commit()
        flash(u"Le tournoi {} a été mis à jour".format(form.name.data), "info")
        return redirect(url_for(".edit_tournament", tournament_id = tournament_id))
    else:
        return render_template("tournament/edit_tournament.html", title = title,
                               form = form, tournament = tournament)


@bp.route("/<tournament_id>/delete")
@manager_required
def delete_tournament(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    tournament.deleted_at = datetime.datetime.now()
    db.session.add(tournament)
    db.session.commit()
    flash(u"Le tournoi {} a été supprimé".format(tournament.name), "info")
    return redirect(url_for(".view_tournaments"))


@bp.route("/<tournament_id>")
@login_required
def view_tournament(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    if tournament.deleted_at:
        abort(404)
    title = u"Tournoi {}".format(tournament.name)
    return render_template("tournament/view_tournament.html", title = title,
                           tournament = tournament)


@bp.route("/")
@login_required
def view_tournaments():
    title = "Tournois"
    page = request.args.get("page", 1, type = int)
    pagination = (Tournament.query.order_by(Tournament.started_at.desc())
                  .filter(Tournament.deleted_at == None)
                  .paginate(page, per_page = current_app.config["TOURNAMENTS_PER_PAGE"], error_out = False))
    return render_template("tournament/view_tournaments.html", title = title,
                           pagination = pagination)


@bp.route("/<tournament_id>/open_registrations")
@manager_required
def open_registrations(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    tournament.status = TournamentStatus.REGISTRATION_OPEN
    db.session.add(tournament)
    db.session.commit()
    flash(REGISTRATION_OPENED, "info")
    return redirect(url_for(".view_tournament", tournament_id = tournament.id))


@bp.route("/<tournament_id>/close_registrations")
@manager_required
def close_registrations(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    tournament.status = TournamentStatus.ONGOING
    db.session.add(tournament)
    db.session.commit()
    flash(REGISTRATION_CLOSED, "info")
    return redirect(url_for(".view_tournament", tournament_id = tournament.id))


@bp.route("/<tournament_id>/register")
@manager_required
def register(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    if not tournament.is_open_to_registration():
        flash(REGISTRATION_NOT_OPEN, "warning")
        return redirect(url_for(".view_tournament", tournament_id = tournament.id))

    if current_user.is_registered_to_tournament(tournament_id):
        flash(ALREADY_REGISTERED, "warning")
        return redirect(url_for(".view_tournament", tournament_id = tournament.id))

    participant = Participant(tournament_id = tournament_id,
                              user_id = current_user.id)
    db.session.add(participant)
    db.session.commit()
    flash(REGISTERED_TO_TOURNAMENT, "info")
    return redirect(url_for(".view_tournament", tournament_id = tournament.id))


@bp.route("/<tournament_id>/draw/<user_id>")
@login_required
def view_participant_draw(tournament_id, user_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    if not tournament.is_visible():
        return redirect(url_for(".view_tournament", tournament_id = tournament_id))
    participant = (Participant.query
                   .filter(Participant.user_id == user_id)
                   .filter(Participant.tournament_id == tournament_id)
                   .first())
    if participant is None:
        return redirect(url_for(".view_tournament", tournament_id = tournament_id))

    return redirect(url_for(".view_tournament", tournament_id = tournament_id))


@bp.route("/<tournament_id>/draw/create", methods = ["GET", "POST"])
@manager_required
def create_tournament_draw(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    if tournament.deleted_at:
        abort(404)
    title = u"Créer le tableau du tournoi"

    matches = tournament.get_matches_first_round()

    if not request.form:
        form = CreateTournamentDrawForm()

        for _ in matches:
            form.player.append_entry()

    else:
        form = CreateTournamentDrawForm(request.form)

    player_names = Player.get_all_players()
    for p in form.player:
        p.player1_name.choices = player_names
        p.player2_name.choices = player_names

    if form.validate_on_submit():
        for match, p in zip(matches, form.player):
            t1 = TournamentPlayer(player_id = p.data["player1_name"],
                                  seed = p.data["player1_seed"],
                                  status = p.data["player1_status"],
                                  position = 0,
                                  tournament_id = tournament_id)
            t2 = TournamentPlayer(player_id = p.data["player2_name"],
                                  seed = p.data["player2_seed"],
                                  status = p.data["player2_status"],
                                  position = 1,
                                  tournament_id = tournament_id)

            # Add tournament players
            db.session.add(t1)
            db.session.add(t2)
            db.session.commit()

            # Link these tournament players to the match
            match.tournament_player1_id = t1.id
            match.tournament_player2_id = t2.id
            db.session.add(match)
            db.session.commit()


        flash("Le tableau du tournoi {} a été créé".format(tournament.name), "info")
        return redirect(url_for(".view_tournament", tournament_id = tournament_id))
    else:
        return render_template("tournament/create_tournament_draw.html", title = title,
                               form = form,
                               tournament = tournament)


@bp.route("/<tournament_id>/draw")
def view_tournament_draw(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    if tournament.deleted_at:
        abort(404)
    title = u"Tableau du tournoi"

    return render_template("tournament/view_tournament_draw.html",
                           title = title,
                           tournament = tournament)


@bp.route("/<tournament_id>/draw/fill", methods = ["GET", "POST"])
def fill_tournament_draw(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    if tournament.deleted_at:
        abort(404)
    title = u"Remplir mon tableau"

    form = FillTournamentDrawForm()

    if form.validate_on_submit():
        flash(form.forecast.data, "info")
        return redirect(url_for(".fill_tournament_draw", tournament_id = tournament_id))

    else:
        return render_template("tournament/fill_tournament_draw.html",
                               title = title,
                               tournament = tournament,
                               form = form)
