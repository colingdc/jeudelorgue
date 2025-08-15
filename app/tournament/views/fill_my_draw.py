import json

from flask import render_template
from flask_login import login_required, current_user

from .. import bp
from .. import domain
from .. import routing
from ..forms import FillTournamentDrawForm
from ...lang import WORDINGS
from ...models import db, Participant, Forecast
from ...utils import display_success_toast, display_warning_toast


@bp.route("/<tournament_id>/draw/<participant_id>/fill", methods=["GET", "POST"])
@login_required
def fill_my_draw(tournament_id, participant_id):
    tournament = domain.get_tournament(tournament_id)
    participant = Participant.query.get_or_404(participant_id)
    if participant.user_id != current_user.id:
        return routing.redirect_to_view_tournament(tournament_id)

    if not tournament.is_open_to_registration():
        return routing.redirect_to_view_tournament(tournament_id)

    title = WORDINGS.TOURNAMENT.FILL_MY_DRAW.format(tournament.name)

    if participant.has_filled_draw():
        return routing.redirect_to_edit_my_draw(tournament_id, participant_id)

    form = FillTournamentDrawForm()

    if form.validate_on_submit():
        forecasts = json.loads(form.forecast.data)
        for match_id, tournament_player_id in forecasts.items():
            if tournament_player_id != "None":
                forecast = Forecast(
                    match_id=match_id,
                    winner_id=tournament_player_id,
                    participant_id=participant_id
                )
            else:
                forecast = Forecast(
                    match_id=match_id,
                    winner_id=None,
                    participant_id=participant_id
                )
            db.session.add(forecast)
        db.session.commit()

        if participant.has_completely_filled_draw():
            display_success_toast(WORDINGS.TOURNAMENT.DRAW_FILLED_COMPLETELY)
        else:
            display_warning_toast(WORDINGS.TOURNAMENT.DRAW_NOT_FILLED_COMPLETELY)
        return routing.redirect_to_view_tournament(tournament_id)

    else:
        return render_template(
            "tournament/fill_my_draw.html",
            title=title,
            tournament=tournament,
            participant=participant,
            form=form,
            surface=tournament.surface.class_name
        ) 
