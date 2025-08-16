from flask import render_template
from flask_babel import _
from flask_login import login_required

from .. import bp
from .. import domain
from .. import routing


@bp.route("/<tournament_id>/stats/forecasts")
@login_required
def overall_forecasts_stats(tournament_id):
    tournament = domain.get_tournament(tournament_id)

    if tournament.are_draws_private():
        return routing.redirect_to_view_tournament(tournament_id)

    title = _("global_forecasts {name}").format(name=tournament.name)

    return render_template(
        "tournament/overall_forecasts_stats.html",
        title=title,
        tournament=tournament,
        surface=tournament.surface.class_name
    ) 
