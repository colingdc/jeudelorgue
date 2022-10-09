# -*- coding: utf-8 -*-

from flask import abort, render_template, redirect, request, url_for, current_app
from flask_login import login_required

from ..lang import WORDINGS
from ..models import (
    Tournament,
    Ranking,
    TournamentStatus,
)

from . import bp
from .forms import RankingForm


@bp.route("/annual")
@login_required
def annual_ranking():
    return redirect(
        url_for(
            "ranking.historical_annual_ranking",
            tournament_id=Tournament.get_latest_finished_tournament().id
        )
    )


@bp.route("/race")
@login_required
def race_ranking():
    return redirect(
        url_for(
            "ranking.historical_race_ranking",
            tournament_id=Tournament.get_latest_finished_tournament().id
        )
    )


@bp.route("/annual/historical/<tournament_id>")
@login_required
def historical_annual_ranking(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    if tournament.deleted_at:
        abort(404)

    if not tournament.is_finished():
        redirect(
            url_for(
                "tournament.view_tournament",
                tournament_id=tournament_id
            )
        )

    page = request.args.get("page", 1, type=int)
    pagination = (Ranking.get_historical_annual_ranking(tournament_id)
                  .paginate(page, per_page=current_app.config["USERS_PER_PAGE"], error_out=False))

    return render_template(
        "ranking/historical_annual_ranking.html",
        title=WORDINGS.RANKING.RACE_RANKING,
        pagination=pagination,
        tournament=tournament
    )


@bp.route("/race/historical/<tournament_id>")
@login_required
def historical_race_ranking(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    if tournament.deleted_at:
        abort(404)

    if not tournament.is_finished():
        redirect(
            url_for(
                "tournament.view_tournament",
                tournament_id=tournament_id
            )
        )

    page = request.args.get("page", 1, type=int)
    pagination = (Ranking.get_historical_race_ranking(tournament_id)
                  .paginate(page, per_page=current_app.config["USERS_PER_PAGE"], error_out=False))

    return render_template(
        "ranking/historical_race_ranking.html",
        title=WORDINGS.RANKING.RACE_RANKING,
        pagination=pagination,
        tournament=tournament
    )


@bp.route("/all", methods=["GET", "POST"])
@login_required
def all_rankings():
    form = RankingForm()
    tournaments = Tournament.query.filter(Tournament.deleted_at.is_(None)).filter(
        Tournament.status == TournamentStatus.FINISHED).order_by(Tournament.ended_at.desc())
    form.tournament_name.choices = [(-1, "Choisir un tournoi...")] + [(t.id, t.name) for t in tournaments]

    tournament_id = request.args.get("tournament_id")
    ranking_type = request.args.get("ranking_type")

    if tournament_id:
        tournament = Tournament.query.get(tournament_id)

    elif form.validate_on_submit():
        tournament = Tournament.query.get(form.tournament_name.data)

    else:
        tournament = None

    if ranking_type:
        pass

    elif form.validate_on_submit():
        ranking_type = form.ranking_type.data

    else:
        ranking_type = None

    if tournament and ranking_type:
        if ranking_type == "race":
            return redirect(
                url_for(
                    ".historical_race_ranking",
                    tournament_id=tournament.id
                )
            )
        elif ranking_type == "annual":
            return redirect(
                url_for(
                    ".historical_annual_ranking",
                    tournament_id=tournament.id
                )
            )

    return render_template(
        "ranking/all_rankings.html",
        title=WORDINGS.RANKING.RANKINGS,
        form=form
    )
