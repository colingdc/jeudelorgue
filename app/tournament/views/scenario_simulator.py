import json

from flask import render_template, request
from flask_login import login_required

from .. import bp
from .. import domain
from .. import routing
from ..forms import FillTournamentDrawForm
from ...models import TournamentPlayer


@bp.route("/<tournament_id>/scenario_simulator", methods=["GET", "POST"])
@login_required
def scenario_simulator(tournament_id):
    tournament = domain.get_tournament(tournament_id)

    if tournament.are_draws_private():
        return routing.redirect_to_view_tournament(tournament_id)

    form = FillTournamentDrawForm()
    scenario = {match.id: match.winner_id or "None" for match in tournament.matches}

    if request.method == "GET":
        form.forecast.data = json.dumps(scenario)
    elif form.validate_on_submit():
        try:
            results = json.loads(form.forecast.data)
            scenario = {int(k): (int(v) if v != "None" else None) for k, v in results.items()}
        except json.decoder.JSONDecodeError:
            return routing.redirect_to_view_tournament(tournament_id)

    scores = [(participant, participant.get_score_simulator(scenario), participant.risk_coefficient) for participant
              in tournament.participants]
    scores = sorted(scores, key=lambda x: (-x[1], -x[2]))

    simulated_matches = {match_id: None if winner_id is None else TournamentPlayer.query.get(winner_id) for
                         match_id, winner_id in scenario.items()}

    return render_template(
        "tournament/scenario_simulator.html",
        title=tournament.name,
        tournament=tournament,
        form=form,
        scenario=scenario,
        scores=scores,
        simulated_matches=simulated_matches,
        surface=tournament.surface.class_name
    )
