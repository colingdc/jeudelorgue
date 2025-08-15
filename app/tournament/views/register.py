from flask_login import login_required, current_user

from .. import bp
from .. import domain
from .. import routing
from ...lang import WORDINGS
from ...models import db, Participant
from ...utils import display_info_toast, display_warning_toast


@bp.route("/<tournament_id>/register")
@login_required
def register(tournament_id):
    tournament = domain.get_tournament(tournament_id)
    if not tournament.is_open_to_registration():
        display_warning_toast(WORDINGS.TOURNAMENT.REGISTRATION_NOT_OPEN)
        return routing.redirect_to_view_tournament(tournament_id)

    if current_user.is_registered_to_tournament(tournament_id):
        display_warning_toast(WORDINGS.TOURNAMENT.ALREADY_REGISTERED)
        return routing.redirect_to_view_tournament(tournament_id)

    participant = Participant(
        tournament_id=tournament_id,
        user_id=current_user.id
    )
    db.session.add(participant)
    db.session.commit()
    display_info_toast(WORDINGS.TOURNAMENT.REGISTERED_TO_TOURNAMENT)
    return routing.redirect_to_view_tournament(tournament.id) 
