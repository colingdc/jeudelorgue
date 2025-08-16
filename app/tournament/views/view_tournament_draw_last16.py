from flask import render_template
from flask_babel import _
from flask_login import login_required

from .. import bp
from .. import domain
from .. import routing


@bp.route("/<tournament_id>/draw/last16")
@login_required
def view_tournament_draw_last16(tournament_id):
    tournament = domain.get_tournament(tournament_id)

    if tournament.number_rounds <= 4:
        return routing.redirect_to_view_tournament_draw(tournament_id)

    return render_template(
        "tournament/view_tournament_draw_last16.html",
        title=_("tournament_draw"),
        tournament=tournament,
        surface=tournament.surface.class_name
    ) 
