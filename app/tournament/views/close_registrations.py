from .. import bp
from .. import domain
from .. import routing
from ...decorators import manager_required
from ...lang import WORDINGS
from ...models import db, TournamentStatus
from ...utils import display_info_toast


@bp.route("/<tournament_id>/close_registrations")
@manager_required
def close_registrations(tournament_id):
    tournament = domain.get_tournament(tournament_id)
    tournament.status = TournamentStatus.ONGOING
    db.session.add(tournament)
    db.session.commit()

    for participant in tournament.participants:
        if not participant.has_filled_draw():
            db.session.delete(participant)
    db.session.commit()

    risk_coefficient_by_participant = domain.compute_risk_coefficient_by_participant(tournament)
    for participant in tournament.participants:
        participant.risk_coefficient = risk_coefficient_by_participant[participant.id]
        db.session.add(participant)
    db.session.commit()

    display_info_toast(WORDINGS.TOURNAMENT.REGISTRATION_CLOSED)
    return routing.redirect_to_view_tournament(tournament.id) 
