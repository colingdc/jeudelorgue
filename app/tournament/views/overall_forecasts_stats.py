from flask import render_template
from flask_login import login_required

from .. import bp
from .. import domain
from .. import routing
from ...lang import WORDINGS


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
