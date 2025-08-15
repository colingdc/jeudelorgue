from flask import render_template

from .. import bp
from .. import domain
from ...decorators import manager_required
from ...lang import WORDINGS


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
