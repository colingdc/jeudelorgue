from flask import redirect, url_for
from flask_login import login_required

from .. import bp
from ...models import Tournament


@bp.route("/race")
@login_required
def race_ranking():
    return redirect(
        url_for(
            "ranking.historical_race_ranking",
            tournament_id=Tournament.get_latest_finished_tournament().id
        )
    ) 
