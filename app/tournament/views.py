import datetime
import json

from flask import (
    current_app,
    render_template,
    request,
)
from flask_login import login_required, current_user

from . import bp
from . import domain
from . import routing
from .forms import (
    CreateTournamentDrawForm,
    CreateTournamentForm,
    EditTournamentForm,
    FillTournamentDrawForm,
    TournamentPlayerAlphabeticStatsForm,
    TournamentPlayerStatsForm,
)
from ..decorators import manager_required
from ..lang import WORDINGS
from ..models import (
    db,
    Forecast,
    Participant,
    Player,
    Tournament,
    TournamentPlayer,
    TournamentStatus,
)
from ..ranking import domain as ranking_domain
from ..utils import display_info_toast, display_success_toast, display_warning_toast


@bp.route("/create", methods=["GET", "POST"])
@manager_required
def create_tournament():
    form = CreateTournamentForm(request.form)
    form.category.choices = domain.get_categories()
    form.surface.choices = domain.get_surfaces()

    if form.validate_on_submit():
        tournament = domain.create_tournament(form)
        display_info_toast(WORDINGS.TOURNAMENT.TOURNAMENT_CREATED.format(form.name.data))
        return routing.redirect_to_view_tournament(tournament.id)
    else:
        return render_template(
            "tournament/create_tournament.html",
            title=WORDINGS.TOURNAMENT.CREATE_TOURNAMENT,
            form=form
        )


@bp.route("/<tournament_id>/edit", methods=["GET", "POST"])
@manager_required
def edit_tournament(tournament_id):
    tournament = domain.get_tournament(tournament_id)
    title = tournament.name
    form = EditTournamentForm(request.form)

    form.category.choices = domain.get_categories()
    form.surface.choices = domain.get_surfaces()

    if request.method == "GET":
        form.name.data = tournament.name
        form.category.data = tournament.category_id
        form.surface.data = tournament.surface_id
        form.start_date.data = tournament.started_at
        form.tournament_topic_url.data = tournament.tournament_topic_url
        form.jeudelorgue_topic_url.data = tournament.jeudelorgue_topic_url
    if form.validate_on_submit():
        domain.edit_tournament(tournament, form)
        display_info_toast(WORDINGS.TOURNAMENT.TOURNAMENT_UPDATED.format(form.name.data))
        return routing.redirect_to_edit_tournament(tournament_id)
    else:
        return render_template(
            "tournament/edit_tournament.html",
            title=title,
            form=form,
            tournament=tournament,
            surface=tournament.surface.class_name
        )


@bp.route("/<tournament_id>/delete")
@manager_required
def delete_tournament(tournament_id):
    tournament = domain.get_tournament(tournament_id)
    tournament.deleted_at = datetime.datetime.now()
    db.session.add(tournament)
    db.session.commit()
    display_info_toast(WORDINGS.TOURNAMENT.TOURNAMENT_DELETED.format(tournament.name))
    return routing.redirect_to_view_tournaments()


@bp.route("/<tournament_id>")
@login_required
def view_tournament(tournament_id):
    tournament = domain.get_tournament(tournament_id)
    title = tournament.name
    return render_template(
        "tournament/view_tournament.html",
        title=title,
        tournament=tournament,
        surface=tournament.surface.class_name
    )


@bp.route("/all")
@login_required
def view_tournaments():
    title = "Tournois"
    page = request.args.get("page", 1, type=int)
    pagination = (Tournament.query.order_by(Tournament.started_at.desc())
                  .filter(Tournament.deleted_at == None)
                  .order_by(Tournament.started_at.desc())
                  .paginate(page=page, per_page=current_app.config["TOURNAMENTS_PER_PAGE"], error_out=False))
    return render_template(
        "tournament/view_tournaments.html",
        title=title,
        pagination=pagination
    )


@bp.route("/<tournament_id>/open_registrations")
@manager_required
def open_registrations(tournament_id):
    tournament = domain.get_tournament(tournament_id)
    tournament.status = TournamentStatus.REGISTRATION_OPEN
    tournament.ended_at = None
    db.session.add(tournament)
    db.session.commit()
    display_info_toast(WORDINGS.TOURNAMENT.REGISTRATION_OPENED)
    return routing.redirect_to_view_tournament(tournament.id)


@bp.route("/<tournament_id>/close_registrations")
@manager_required
def close_registrations(tournament_id):
    tournament = domain.get_tournament(tournament_id)
    tournament.status = TournamentStatus.ONGOING
    db.session.add(tournament)
    db.session.commit()

    for participant in tournament.participants:
        if not participant.has_filled_draw():
            db.session.delete(participant)
    db.session.commit()

    risk_coefficient_by_participant = domain.compute_risk_coefficient_by_participant(tournament)
    for participant in tournament.participants:
        participant.risk_coefficient = risk_coefficient_by_participant[participant.id]
        db.session.add(participant)
    db.session.commit()

    display_info_toast(WORDINGS.TOURNAMENT.REGISTRATION_CLOSED)
    return routing.redirect_to_view_tournament(tournament.id)


@bp.route("/<tournament_id>/close_tournament")
@manager_required
def close_tournament(tournament_id):
    tournament = domain.get_tournament(tournament_id)
    tournament.status = TournamentStatus.FINISHED
    tournament.ended_at = datetime.datetime.now()
    db.session.add(tournament)
    db.session.commit()

    scores = tournament.distribute_points()
    for rank, participant in enumerate(tournament.participants_sorted()):
        participant.points = scores[participant]
        participant.user.annual_points = participant.user.get_annual_points()
        participant.user.year_to_date_points = participant.user.get_year_to_date_points()
        participant.ranking = rank + 1
        db.session.add(participant)
    db.session.commit()

    ranking_domain.compute_historical_rankings(tournament)

    display_info_toast(WORDINGS.TOURNAMENT.TOURNAMENT_CLOSED)
    return routing.redirect_to_view_tournament(tournament.id)


@bp.route("/<tournament_id>/register")
@login_required
def register(tournament_id):
    tournament = domain.get_tournament(tournament_id)
    if not tournament.is_open_to_registration():
        display_warning_toast(WORDINGS.TOURNAMENT.REGISTRATION_NOT_OPEN)
        return routing.redirect_to_view_tournament(tournament_id)

    if current_user.is_registered_to_tournament(tournament_id):
        display_warning_toast(WORDINGS.TOURNAMENT.ALREADY_REGISTERED)
        return routing.redirect_to_view_tournament(tournament_id)

    participant = Participant(
        tournament_id=tournament_id,
        user_id=current_user.id
    )
    db.session.add(participant)
    db.session.commit()
    display_info_toast(WORDINGS.TOURNAMENT.REGISTERED_TO_TOURNAMENT)
    return routing.redirect_to_view_tournament(tournament.id)


@bp.route("/<tournament_id>/draw/create", methods=["GET", "POST"])
@manager_required
def create_tournament_draw(tournament_id):
    tournament = domain.get_tournament(tournament_id)
    title = "{} - Créer le tableau".format(tournament.name)

    matches = tournament.get_matches_first_round()

    if not request.form:
        form = CreateTournamentDrawForm()

        for _ in matches:
            form.player.append_entry()

    else:
        form = CreateTournamentDrawForm(request.form)

    player_names = [(-1, WORDINGS.PLAYER.CHOOSE_PLAYER)] + Player.get_all_players()

    for p in form.player:
        p.player1_name.choices = player_names
        p.player2_name.choices = player_names

    if form.validate_on_submit():
        domain.create_tournament_draw(tournament, matches, form)

        display_info_toast(WORDINGS.TOURNAMENT.TOURNAMENT_DRAW_CREATED.format(tournament.name))
        return routing.redirect_to_view_tournament(tournament_id)
    else:
        return render_template(
            "tournament/create_tournament_draw.html",
            title=title,
            form=form,
            tournament=tournament,
            surface=tournament.surface.class_name
        )


@bp.route("/<tournament_id>/draw/edit", methods=["GET", "POST"])
@manager_required
def edit_tournament_draw(tournament_id):
    tournament = domain.get_tournament(tournament_id)
    matches = tournament.get_matches_first_round()

    if not request.form:
        form = CreateTournamentDrawForm()

        for _ in matches:
            form.player.append_entry()

    else:
        form = CreateTournamentDrawForm(request.form)

    player_names = [(-1, WORDINGS.PLAYER.CHOOSE_PLAYER)] + Player.get_all_players()

    for p in form.player:
        p.player1_name.choices = player_names
        p.player2_name.choices = player_names

    if request.method == "GET":
        for p, match in zip(form.player, matches):
            if match.tournament_player1:
                if match.tournament_player1.player:
                    p.player1_name.data = match.tournament_player1.player.id
                p.player1_status.data = match.tournament_player1.status
                p.player1_seed.data = match.tournament_player1.seed
            if match.tournament_player2:
                if match.tournament_player2.player:
                    p.player2_name.data = match.tournament_player2.player.id
                p.player2_status.data = match.tournament_player2.status
                p.player2_seed.data = match.tournament_player2.seed

    if form.validate_on_submit():
        domain.edit_tournament_draw(tournament, matches, form)

        display_info_toast(WORDINGS.TOURNAMENT.TOURNAMENT_DRAW_UPDATED.format(tournament.name))
        return routing.redirect_to_view_tournament(tournament_id)
    else:
        return render_template(
            "tournament/edit_tournament_draw.html",
            title=WORDINGS.TOURNAMENT.CREATE_TOURNAMENT_DRAW,
            form=form,
            tournament=tournament,
            surface=tournament.surface.class_name
        )


@bp.route("/<tournament_id>/draw")
@login_required
def view_tournament_draw(tournament_id):
    tournament = domain.get_tournament(tournament_id)

    return render_template(
        "tournament/view_tournament_draw.html",
        title=WORDINGS.TOURNAMENT.TOURNAMENT_DRAW,
        tournament=tournament,
        surface=tournament.surface.class_name
    )


@bp.route("/<tournament_id>/draw/last16")
@login_required
def view_tournament_draw_last16(tournament_id):
    tournament = domain.get_tournament(tournament_id)

    if tournament.number_rounds <= 4:
        return routing.redirect_to_view_tournament_draw(tournament_id)

    return render_template(
        "tournament/view_tournament_draw_last16.html",
        title=WORDINGS.TOURNAMENT.TOURNAMENT_DRAW,
        tournament=tournament,
        surface=tournament.surface.class_name
    )


@bp.route("/<tournament_id>/draw/update", methods=["GET", "POST"])
@manager_required
def update_tournament_draw(tournament_id):
    tournament = domain.get_tournament(tournament_id)

    form = FillTournamentDrawForm()

    if form.validate_on_submit():
        try:
            results = json.loads(form.forecast.data)
        except json.decoder.JSONDecodeError:
            return routing.redirect_to_view_tournament(tournament_id)

        matches = tournament.matches

        for match in matches:
            winner_id = results[str(match.id)]
            next_match = match.get_next_match()
            if winner_id == "None":
                match.winner_id = None
                if next_match:
                    if match.position % 2 == 0:
                        next_match.tournament_player1_id = None
                    else:
                        next_match.tournament_player2_id = None
                    db.session.add(next_match)
            else:
                match.winner_id = winner_id
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

        for rank, participant in enumerate(tournament.participants_sorted()):
            participant.ranking = rank + 1
            db.session.add(participant)
        db.session.commit()

        tournament.current_maximal_score = tournament.get_current_maximal_score()
        db.session.add(tournament)
        db.session.commit()

        return routing.redirect_to_view_tournament(tournament_id)

    else:
        return render_template(
            "tournament/update_tournament_draw.html",
            title=WORDINGS.TOURNAMENT.UPDATE_TOURNAMENT_DRAW,
            tournament=tournament,
            form=form,
            surface=tournament.surface.class_name
        )


@bp.route("/<tournament_id>/draw/<participant_id>/fill", methods=["GET", "POST"])
@login_required
def fill_my_draw(tournament_id, participant_id):
    tournament = domain.get_tournament(tournament_id)
    participant = Participant.query.get_or_404(participant_id)
    if participant.user_id != current_user.id:
        return routing.redirect_to_view_tournament(tournament_id)

    if not tournament.is_open_to_registration():
        return routing.redirect_to_view_tournament(tournament_id)

    title = WORDINGS.TOURNAMENT.FILL_MY_DRAW.format(tournament.name)

    if participant.has_filled_draw():
        return routing.redirect_to_edit_my_draw(tournament_id, participant_id)

    form = FillTournamentDrawForm()

    if form.validate_on_submit():
        forecasts = json.loads(form.forecast.data)
        for match_id, tournament_player_id in forecasts.items():
            if tournament_player_id != "None":
                forecast = Forecast(
                    match_id=match_id,
                    winner_id=tournament_player_id,
                    participant_id=participant_id
                )
            else:
                forecast = Forecast(
                    match_id=match_id,
                    winner_id=None,
                    participant_id=participant_id
                )
            db.session.add(forecast)
        db.session.commit()

        if participant.has_completely_filled_draw():
            display_success_toast(WORDINGS.TOURNAMENT.DRAW_FILLED_COMPLETELY)
        else:
            display_warning_toast(WORDINGS.TOURNAMENT.DRAW_NOT_FILLED_COMPLETELY)
        return routing.redirect_to_view_tournament(tournament_id)

    else:
        return render_template(
            "tournament/fill_my_draw.html",
            title=title,
            tournament=tournament,
            participant=participant,
            form=form,
            surface=tournament.surface.class_name
        )


@bp.route("/<tournament_id>/draw/<participant_id>/edit", methods=["GET", "POST"])
@login_required
def edit_my_draw(tournament_id, participant_id):
    tournament = domain.get_tournament(tournament_id)
    participant = Participant.query.get_or_404(participant_id)
    if participant.user_id != current_user.id:
        return routing.redirect_to_view_tournament(tournament_id)

    if not tournament.is_open_to_registration():
        return routing.redirect_to_view_tournament(tournament_id)

    title = "{} - Modifier mon tableau".format(tournament.name)
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

        if participant.has_completely_filled_draw():
            display_success_toast(WORDINGS.TOURNAMENT.DRAW_FILLED_COMPLETELY)
        else:
            display_warning_toast(WORDINGS.TOURNAMENT.DRAW_NOT_FILLED_COMPLETELY)
        return routing.redirect_to_view_tournament(tournament_id)

    else:
        return render_template(
            "tournament/edit_my_draw.html",
            title=title,
            tournament=tournament,
            participant=participant,
            form=form,
            surface=tournament.surface.class_name
        )


@bp.route("/<tournament_id>/draw/<participant_id>")
@login_required
def view_participant_draw(tournament_id, participant_id):
    tournament = domain.get_tournament(tournament_id)
    participant = Participant.query.get_or_404(participant_id)

    if tournament.are_draws_private():
        if participant.user_id != current_user.id:
            return routing.redirect_to_view_tournament(tournament_id)

    title = WORDINGS.TOURNAMENT.PARTICIPANT_DRAW.format(tournament.name, participant.user.username)

    return render_template(
        "tournament/view_participant_draw.html",
        title=title,
        tournament=tournament,
        participant=participant,
        surface=tournament.surface.class_name
    )


@bp.route("/<tournament_id>/draw/<participant_id>/last16")
@login_required
def view_participant_draw_last16(tournament_id, participant_id):
    tournament = domain.get_tournament(tournament_id)

    if tournament.number_rounds <= 4:
        return routing.redirect_to_view_participant_draw(tournament_id, participant_id)

    participant = Participant.query.get_or_404(participant_id)

    if tournament.are_draws_private():
        if participant.user_id != current_user.id:
            return routing.redirect_to_view_tournament(tournament_id)

    title = WORDINGS.TOURNAMENT.PARTICIPANT_DRAW.format(tournament.name, participant.user.username)

    return render_template(
        "tournament/view_participant_draw_last16.html",
        title=title,
        tournament=tournament,
        participant=participant,
        surface=tournament.surface.class_name
    )


@bp.route("/<tournament_id>/stats/tournament_players", methods=["GET", "POST"])
@login_required
def tournament_player_stats(tournament_id):
    tournament = domain.get_tournament(tournament_id)

    if tournament.are_draws_private():
        return routing.redirect_to_view_tournament(tournament_id)

    title = WORDINGS.TOURNAMENT.FORECAST_BY_PLAYER.format(tournament.name)

    form = TournamentPlayerStatsForm()
    tournament_players = [(-1, WORDINGS.PLAYER.CHOOSE_PLAYER)] + [
        (p.id, p.get_full_name())
        for p in tournament.players
        if (p.player is None or p.player.last_name.lower() != "bye")
    ]
    form.player_name.choices = tournament_players

    form_alphabetic = TournamentPlayerAlphabeticStatsForm()
    tournament_players_alphabetic = [(-1, WORDINGS.PLAYER.CHOOSE_PLAYER)] + [
        (p.id, p.get_full_name_surname_first())
        for p in tournament.players_alphabetic
        if (p.player is None or p.player.last_name.lower() != "bye")
    ]
    form_alphabetic.player_name.choices = tournament_players_alphabetic

    tournament_player_id = request.args.get("tournament_player_id")

    if tournament_player_id:
        tournament_player = TournamentPlayer.query.get(tournament_player_id)

    elif form.validate_on_submit():
        tournament_player = TournamentPlayer.query.get(form.player_name.data)

    elif form_alphabetic.validate_on_submit():
        tournament_player = TournamentPlayer.query.get(form_alphabetic.player_name.data)

    else:
        tournament_player = None

    return render_template(
        "tournament/tournament_player_stats.html",
        title=title,
        tournament=tournament,
        form=form,
        form_alphabetic=form_alphabetic,
        tournament_player=tournament_player,
        surface=tournament.surface.class_name
    )


@bp.route("/<tournament_id>/stats/forecasts")
@login_required
def overall_forecasts_stats(tournament_id):
    tournament = domain.get_tournament(tournament_id)

    if tournament.are_draws_private():
        return routing.redirect_to_view_tournament(tournament_id)

    title = WORDINGS.TOURNAMENT.GLOBAL_FORECASTS.format(tournament.name)

    return render_template(
        "tournament/overall_forecasts_stats.html",
        title=title,
        tournament=tournament,
        surface=tournament.surface.class_name
    )


@bp.route("/current")
@login_required
def current_tournament():
    tournament = domain.get_current_tournament()
    if tournament:
        return routing.redirect_to_view_tournament(tournament.id)
    else:
        return routing.redirect_to_view_tournaments()


@bp.route("/<tournament_id>/scenario_simulator", methods=["GET", "POST"])
@login_required
def scenario_simulator(tournament_id):
    tournament = domain.get_tournament(tournament_id)

    if tournament.are_draws_private():
        return routing.redirect_to_view_tournament(tournament_id)

    title = WORDINGS.TOURNAMENT.SCENARIO_SIMULATOR.format(tournament.name)

    form = FillTournamentDrawForm()

    if request.method == "GET":
        scenario = {match.id: match.winner_id or "None" for match in tournament.matches}
        form.forecast.data = json.dumps(scenario)
        scenario = {int(k): (int(v) if v != "None" else None) for k, v in scenario.items()}

        scores = [(participant, participant.get_score_simulator(scenario), participant.risk_coefficient) for participant
                  in tournament.participants]
        scores = sorted(scores, key=lambda x: (-x[1], -x[2]))

        simulated_matches = {match_id: None if winner_id is None else TournamentPlayer.query.get(winner_id) for
                             match_id, winner_id in scenario.items()}

    if form.validate_on_submit():
        try:
            results = json.loads(form.forecast.data)
        except json.decoder.JSONDecodeError:
            return routing.redirect_to_view_tournament(tournament_id)
        scenario = {int(k): (int(v) if v != "None" else None) for k, v in results.items()}

        scores = [(participant, participant.get_score_simulator(scenario), participant.risk_coefficient) for participant
                  in tournament.participants]
        scores = sorted(scores, key=lambda x: (-x[1], -x[2]))

        simulated_matches = {match_id: None if winner_id is None else TournamentPlayer.query.get(winner_id) for
                             match_id, winner_id in scenario.items()}

        return render_template(
            "tournament/scenario_simulator.html",
            title=title,
            tournament=tournament,
            form=form,
            scenario=scenario,
            scores=scores,
            simulated_matches=simulated_matches,
            surface=tournament.surface.class_name
        )

    else:
        return render_template(
            "tournament/scenario_simulator.html",
            title=title,
            tournament=tournament,
            form=form,
            scenario=scenario,
            scores=scores,
            simulated_matches=simulated_matches,
            surface=tournament.surface.class_name
        )


@bp.route("/<tournament_id>/ranking/raw")
@manager_required
def raw_tournament_ranking(tournament_id):
    tournament = domain.get_tournament(tournament_id)

    title = WORDINGS.RANKING.RAW_RANKING.format(tournament.name)

    return render_template(
        "tournament/raw_tournament_ranking.html",
        title=title,
        tournament=tournament
    )
