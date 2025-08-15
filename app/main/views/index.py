from flask import render_template

from .. import bp
from ...lang import WORDINGS
from ...models import Tournament, Ranking
from ...tournament import domain as tournament_domain


@bp.route("/index")
def index():
    tournaments = Tournament.get_recent_tournaments(20)
    current_tournament = tournament_domain.get_current_tournament()
    latest_tournament = Tournament.get_latest_finished_tournament()
    race_ranking = Ranking.get_historical_race_ranking(latest_tournament.id).limit(20)

    return render_template(
        "main/index.html",
        title=WORDINGS.MAIN.HOMEPAGE,
        tournaments=tournaments,
        current_tournament=current_tournament,
        race_ranking=race_ranking
    ) 
