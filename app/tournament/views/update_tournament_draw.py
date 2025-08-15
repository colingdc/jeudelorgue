import json

from flask import render_template

from .. import bp
from .. import domain
from .. import routing
from ..forms import FillTournamentDrawForm
from ...decorators import manager_required
from ...lang import WORDINGS
from ...models import db


@bp.route("/<tournament_id>/draw/update", methods=["GET", "POST"])
@manager_required
def update_tournament_draw(tournament_id):
    tournament = domain.get_tournament(tournament_id)

    form = FillTournamentDrawForm()

    if form.validate_on_submit():
        try:
            results = json.loads(form.forecast.data)
        except json.decoder.JSONDecodeError:
            return routing.redirect_to_view_tournament(tournament_id)

        matches = tournament.matches

        for match in matches:
            winner_id = results[str(match.id)]
            next_match = match.get_next_match()
            if winner_id == "None":
                match.winner_id = None
                if next_match:
                    if match.position % 2 == 0:
                        next_match.tournament_player1_id = None
                    else:
                        next_match.tournament_player2_id = None
                    db.session.add(next_match)
            else:
                match.winner_id = winner_id
                if next_match:
                    if match.position % 2 == 0:
                        next_match.tournament_player1_id = winner_id
                    else:
                        next_match.tournament_player2_id = winner_id
                    db.session.add(next_match)

            db.session.add(match)
        db.session.commit()

        for participant in tournament.participants:
            participant.score = participant.get_score()
            db.session.add(participant)
        db.session.commit()

        for rank, participant in enumerate(tournament.participants_sorted()):
            participant.ranking = rank + 1
            db.session.add(participant)
        db.session.commit()

        tournament.current_maximal_score = tournament.get_current_maximal_score()
        db.session.add(tournament)
        db.session.commit()

        return routing.redirect_to_view_tournament(tournament_id)

    else:
        return render_template(
            "tournament/update_tournament_draw.html",
            title=WORDINGS.TOURNAMENT.UPDATE_TOURNAMENT_DRAW,
            tournament=tournament,
            form=form,
            surface=tournament.surface.class_name
        ) 
