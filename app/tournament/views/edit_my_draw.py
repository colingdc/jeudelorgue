import json

from flask import render_template
from flask_babel import gettext as _
from flask_login import login_required, current_user

from .. import bp
from .. import domain
from .. import routing
from ..forms import FillTournamentDrawForm
from ...models import db, Participant
from ...utils import display_success_toast, display_warning_toast


@bp.route("/<tournament_id>/draw/<participant_id>/edit", methods=["GET", "POST"])
@login_required
def edit_my_draw(tournament_id, participant_id):
    tournament = domain.get_tournament(tournament_id)
    participant = Participant.query.get_or_404(participant_id)
    if participant.user_id != current_user.id:
        return routing.redirect_to_view_tournament(tournament_id)

    if not tournament.is_open_to_registration():
        return routing.redirect_to_view_tournament(tournament_id)

    form = FillTournamentDrawForm()

    if form.validate_on_submit():
        forecasts = json.loads(form.forecast.data)
        current_forecasts = participant.forecasts

        for current_forecast in current_forecasts:
            winner_id = forecasts[str(current_forecast.match_id)]
            if winner_id == "None":
                current_forecast.winner_id = None
            else:
                current_forecast.winner_id = winner_id
            db.session.add(current_forecast)
        db.session.commit()

        if participant.has_completely_filled_draw():
            display_success_toast(_("draw_filled_completely"))
        else:
            display_warning_toast(_("draw_not_filled_completely"))
        return routing.redirect_to_view_tournament(tournament_id)

    else:
        return render_template(
            "tournament/edit_my_draw.html",
            title=tournament.name,
            tournament=tournament,
            participant=participant,
            form=form,
            surface=tournament.surface.class_name
        ) 
