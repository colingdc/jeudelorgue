from flask_babel import _

from .. import bp
from .. import domain
from .. import routing
from ...decorators import manager_required
from ...models import db, TournamentStatus
from ...utils import display_info_toast


@bp.route("/<tournament_id>/open_registrations")
@manager_required
def open_registrations(tournament_id):
    tournament = domain.get_tournament(tournament_id)
    tournament.status = TournamentStatus.REGISTRATION_OPEN
    tournament.ended_at = None
    db.session.add(tournament)
    db.session.commit()
    display_info_toast(_("registration_opened"))
    return routing.redirect_to_view_tournament(tournament.id) 
