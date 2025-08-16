from flask import render_template
from flask_login import login_required

from .. import bp
from .. import domain


@bp.route("/<tournament_id>")
@login_required
def view_tournament(tournament_id):
    tournament = domain.get_tournament(tournament_id)

    return render_template(
        "tournament/view_tournament.html",
        title=tournament.name,
        tournament=tournament,
        surface=tournament.surface.class_name
    ) 

