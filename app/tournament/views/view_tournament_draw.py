from flask import render_template
from flask_login import login_required

from .. import bp
from .. import domain
from ...lang import WORDINGS


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
