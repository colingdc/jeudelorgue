# -*- coding: utf-8 -*-

from flask import render_template, redirect, request, flash, url_for, current_app, abort
from flask_login import login_required, current_user
import datetime
from math import log, floor
import json

from . import bp
from .forms import CreateTournamentForm, EditTournamentForm, CreateTournamentDrawForm, PlayerTournamentDrawForm, FillTournamentDrawForm
from .. import db
from ..decorators import manager_required
from ..models import Tournament, TournamentStatus, Participant, Match, TournamentPlayer, Player, Forecast, TournamentCategory
from ..texts import (REGISTRATION_CLOSED, REGISTRATION_OPENED, REGISTERED_TO_TOURNAMENT, REGISTRATION_NOT_OPEN,
                     ALREADY_REGISTERED)


@bp.route("/create", methods = ["GET", "POST"])
@manager_required
def create_tournament():
    title = u"Créer un tournoi"
    form = CreateTournamentForm(request.form)

    categories = TournamentCategory.get_all_categories()
    form.category.choices = categories

    if form.validate_on_submit():
        tournament = Tournament(name = form.name.data,
                                started_at = form.start_date.data,
                                category_id = form.category.data)
        db.session.add(tournament)
        db.session.commit()
        for i in range(1, 2 ** tournament.number_rounds):
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

    categories = TournamentCategory.get_all_categories()
    form.category.choices = categories

    if request.method == "GET":
        form.name.data = tournament.name
        form.category.data = tournament.category_id
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
@login_required
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
@login_required
def view_tournament_draw(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    if tournament.deleted_at:
        abort(404)
    title = u"Tableau du tournoi"

    return render_template("tournament/view_tournament_draw.html",
                           title = title,
                           tournament = tournament)


@bp.route("/<tournament_id>/draw/edit", methods = ["GET", "POST"])
@manager_required
def edit_tournament_draw(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    if tournament.deleted_at:
        abort(404)
    title = u"Mettre à jour le tableau du tournoi"

    form = FillTournamentDrawForm()

    if form.validate_on_submit():
        try:
            results = json.loads(form.forecast.data)
        except json.decoder.JSONDecodeError:
            return redirect(url_for(".view_tournament", tournament_id = tournament_id))

        matches = tournament.matches

        for match in matches:
            winner_id = results[str(match.id)]
            if winner_id == "None":
                match.winner_id = None
            else:
                match.winner_id = winner_id
                next_match = match.get_next_match()
                if next_match:
                    if match.position % 2 == 0:
                        next_match.tournament_player1_id = winner_id
                    else:
                        next_match.tournament_player2_id = winner_id
                    db.session.add(next_match)

            db.session.add(match)
        db.session.commit()

        for participant in tournament.participants:
            participant.score = participant.get_score()
            db.session.add(participant)
        db.session.commit()

        return redirect(url_for(".view_tournament", tournament_id = tournament_id))

    else:
        return render_template("tournament/edit_tournament_draw.html",
                               title = title,
                               tournament = tournament,
                               form = form)


@bp.route("/<tournament_id>/draw/<participant_id>/fill", methods = ["GET", "POST"])
@login_required
def fill_my_draw(tournament_id, participant_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    if tournament.deleted_at:
        abort(404)
    participant = Participant.query.get_or_404(participant_id)
    if participant.user_id != current_user.id:
        return redirect(url_for(".view_tournament", tournament_id = tournament_id))

    if not tournament.is_open_to_registration():
        return redirect(url_for(".view_tournament", tournament_id = tournament_id))

    title = u"Remplir mon tableau"

    if participant.has_filled_draw():
        return redirect(url_for(".edit_my_draw", tournament_id = tournament_id, participant_id = participant_id))

    form = FillTournamentDrawForm()

    if form.validate_on_submit():
        forecasts = json.loads(form.forecast.data)
        for match_id, tournament_player_id in forecasts.items():
            if tournament_player_id != "None":
                forecast = Forecast(match_id = match_id,
                                    winner_id = tournament_player_id,
                                    participant_id = participant_id)
            else:
                forecast = Forecast(match_id = match_id,
                                    winner_id = None,
                                    participant_id = participant_id)
            db.session.add(forecast)
        db.session.commit()
        return redirect(url_for(".view_tournament", tournament_id = tournament_id))

    else:
        return render_template("tournament/fill_my_draw.html",
                               title = title,
                               tournament = tournament,
                               participant = participant,
                               form = form)


@bp.route("/<tournament_id>/draw/<participant_id>/edit", methods = ["GET", "POST"])
@login_required
def edit_my_draw(tournament_id, participant_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    if tournament.deleted_at:
        abort(404)
    participant = Participant.query.get_or_404(participant_id)
    if participant.user_id != current_user.id:
        return redirect(url_for(".view_tournament", tournament_id = tournament_id))

    if not tournament.is_open_to_registration():
        return redirect(url_for(".view_tournament", tournament_id = tournament_id))

    title = u"Modifier mon tableau"
    form = FillTournamentDrawForm()

    if form.validate_on_submit():
        forecasts = json.loads(form.forecast.data)
        current_forecasts = participant.forecasts

        for current_forecast in current_forecasts:
            winner_id = forecasts[str(current_forecast.match_id)]
            if winner_id == "None":
                current_forecast.winner_id = None
            else:
                current_forecast.winner_id = winner_id
            db.session.add(current_forecast)
        db.session.commit()

        return redirect(url_for(".view_tournament", tournament_id = tournament_id))

    else:
        return render_template("tournament/edit_my_draw.html",
                               title = title,
                               tournament = tournament,
                               participant = participant,
                               form = form)


@bp.route("/<tournament_id>/draw/<participant_id>")
@login_required
def view_participant_draw(tournament_id, participant_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    if tournament.deleted_at:
        abort(404)
    participant = Participant.query.get_or_404(participant_id)

    if tournament.are_draws_private():
        if participant.user_id != current_user.id:
            return redirect(url_for(".view_tournament", tournament_id = tournament_id))

    title = u"Tableau"

    return render_template("tournament/view_participant_draw.html",
                           title = title,
                           tournament = tournament,
                           participant = participant)
