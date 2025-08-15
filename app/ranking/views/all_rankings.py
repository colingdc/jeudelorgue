from flask import render_template, redirect, request, url_for
from flask_login import login_required

from .. import bp
from ..forms import RankingForm
from ...lang import WORDINGS
from ...models import Tournament, TournamentStatus


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
