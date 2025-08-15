import datetime

from .. import bp
from .. import domain
from .. import routing
from ...decorators import manager_required
from ...lang import WORDINGS
from ...models import db, TournamentStatus
from ...ranking import domain as ranking_domain
from ...utils import display_info_toast


@bp.route("/<tournament_id>/close_tournament")
@manager_required
def close_tournament(tournament_id):
    tournament = domain.get_tournament(tournament_id)
    tournament.status = TournamentStatus.FINISHED
    tournament.ended_at = datetime.datetime.now()
    db.session.add(tournament)
    db.session.commit()

    scores = tournament.distribute_points()
    for rank, participant in enumerate(tournament.participants_sorted()):
        participant.points = scores[participant]
        participant.user.annual_points = participant.user.get_annual_points()
        participant.user.year_to_date_points = participant.user.get_year_to_date_points()
        participant.ranking = rank + 1
        db.session.add(participant)
    db.session.commit()

    ranking_domain.compute_historical_rankings(tournament)

    display_info_toast(WORDINGS.TOURNAMENT.TOURNAMENT_CLOSED)
    return routing.redirect_to_view_tournament(tournament.id) 
