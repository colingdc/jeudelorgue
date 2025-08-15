from flask import render_template
from flask_login import login_required, current_user

from .. import bp
from .. import domain
from .. import routing
from ...lang import WORDINGS
from ...models import Participant


@bp.route("/<tournament_id>/draw/<participant_id>")
@login_required
def view_participant_draw(tournament_id, participant_id):
    tournament = domain.get_tournament(tournament_id)
    participant = Participant.query.get_or_404(participant_id)

    if tournament.are_draws_private():
        if participant.user_id != current_user.id:
            return routing.redirect_to_view_tournament(tournament_id)

    title = WORDINGS.TOURNAMENT.PARTICIPANT_DRAW.format(tournament.name, participant.user.username)

    return render_template(
        "tournament/view_participant_draw.html",
        title=title,
        tournament=tournament,
        participant=participant,
        surface=tournament.surface.class_name
    ) 
