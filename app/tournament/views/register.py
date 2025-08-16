from flask_babel import gettext as _
from flask_login import login_required, current_user

from .. import bp
from .. import domain
from .. import routing
from ...models import db, Participant
from ...utils import display_info_toast, display_warning_toast


@bp.route("/<tournament_id>/register")
@login_required
def register(tournament_id):
    tournament = domain.get_tournament(tournament_id)
    if not tournament.is_open_to_registration():
        display_warning_toast(_("registration_not_open"))
        return routing.redirect_to_view_tournament(tournament_id)

    if current_user.is_registered_to_tournament(tournament_id):
        display_warning_toast(_("already_registered"))
        return routing.redirect_to_view_tournament(tournament_id)

    participant = Participant(
        tournament_id=tournament_id,
        user_id=current_user.id
    )
    db.session.add(participant)
    db.session.commit()
    display_info_toast(_("registered_to_tournament"))
    return routing.redirect_to_view_tournament(tournament.id) 
