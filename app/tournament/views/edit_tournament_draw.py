from flask import render_template, request

from .. import bp
from .. import domain
from .. import routing
from ..forms import CreateTournamentDrawForm
from ...decorators import manager_required
from ...lang import WORDINGS
from ...models import Player
from ...utils import display_info_toast


@bp.route("/<tournament_id>/draw/edit", methods=["GET", "POST"])
@manager_required
def edit_tournament_draw(tournament_id):
    tournament = domain.get_tournament(tournament_id)
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

    if request.method == "GET":
        for p, match in zip(form.player, matches):
            if match.tournament_player1:
                if match.tournament_player1.player:
                    p.player1_name.data = match.tournament_player1.player.id
                p.player1_status.data = match.tournament_player1.status
                p.player1_seed.data = match.tournament_player1.seed
            if match.tournament_player2:
                if match.tournament_player2.player:
                    p.player2_name.data = match.tournament_player2.player.id
                p.player2_status.data = match.tournament_player2.status
                p.player2_seed.data = match.tournament_player2.seed

    if form.validate_on_submit():
        domain.edit_tournament_draw(tournament, matches, form)

        display_info_toast(WORDINGS.TOURNAMENT.TOURNAMENT_DRAW_UPDATED.format(tournament.name))
        return routing.redirect_to_view_tournament(tournament_id)
    else:
        return render_template(
            "tournament/edit_tournament_draw.html",
            title=WORDINGS.TOURNAMENT.CREATE_TOURNAMENT_DRAW,
            form=form,
            tournament=tournament,
            surface=tournament.surface.class_name
        ) 
