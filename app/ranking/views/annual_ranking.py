from flask import redirect, url_for
from flask_login import login_required

from .. import bp
from ...models import Tournament


@bp.route("/annual")
@login_required
def annual_ranking():
    return redirect(
        url_for(
            "ranking.historical_annual_ranking",
            tournament_id=Tournament.get_latest_finished_tournament().id
        )
    ) 
