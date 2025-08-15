from flask import render_template, request

from .. import bp
from .. import domain
from .. import routing
from ..forms import CreateTournamentDrawForm
from ...decorators import manager_required
from ...lang import WORDINGS
from ...models import Player
from ...utils import display_info_toast


@bp.route("/<tournament_id>/draw/create", methods=["GET", "POST"])
@manager_required
def create_tournament_draw(tournament_id):
    tournament = domain.get_tournament(tournament_id)
    title = "{} - Créer le tableau".format(tournament.name)

    matches = tournament.get_matches_first_round()

    if not request.form:
        form = CreateTournamentDrawForm()

        for _ in matches:
            form.player.append_entry()

    else:
        form = CreateTournamentDrawForm(request.form)

    player_names = [(-1, WORDINGS.PLAYER.CHOOSE_PLAYER)] + Player.get_all_players()

    for p in form.player:
        p.player1_name.choices = player_names
        p.player2_name.choices = player_names

    if form.validate_on_submit():
        domain.create_tournament_draw(tournament, matches, form)

        display_info_toast(WORDINGS.TOURNAMENT.TOURNAMENT_DRAW_CREATED.format(tournament.name))
        return routing.redirect_to_view_tournament(tournament_id)
    else:
        return render_template(
            "tournament/create_tournament_draw.html",
            title=title,
            form=form,
            tournament=tournament,
            surface=tournament.surface.class_name
        ) 
