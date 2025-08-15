from flask import abort, render_template, redirect, request, url_for, current_app
from flask_login import login_required

from .. import bp
from ...lang import WORDINGS
from ...models import Tournament, Ranking


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
                  .paginate(page=page, per_page=current_app.config["USERS_PER_PAGE"], error_out=False))

    return render_template(
        "ranking/historical_race_ranking.html",
        title=WORDINGS.RANKING.RACE_RANKING,
        pagination=pagination,
        tournament=tournament
    ) 
