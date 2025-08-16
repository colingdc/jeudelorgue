from flask import render_template, request
from flask_babel import _
from flask_login import login_required

from .. import bp
from .. import domain
from .. import routing
from ..forms import TournamentPlayerStatsForm, TournamentPlayerAlphabeticStatsForm
from ...models import TournamentPlayer


@bp.route("/<tournament_id>/stats/tournament_players", methods=["GET", "POST"])
@login_required
def tournament_player_stats(tournament_id):
    tournament = domain.get_tournament(tournament_id)

    if tournament.are_draws_private():
        return routing.redirect_to_view_tournament(tournament_id)

    form = TournamentPlayerStatsForm()
    form.player_name.choices = build_player_choices(tournament.players)

    form_alphabetic = TournamentPlayerAlphabeticStatsForm()
    form_alphabetic.player_name.choices = build_player_choices(tournament.players_alphabetic)

    tournament_player_id = request.args.get("tournament_player_id")

    if tournament_player_id:
        tournament_player = TournamentPlayer.query.get(tournament_player_id)

    elif form.validate_on_submit():
        tournament_player = TournamentPlayer.query.get(form.player_name.data)

    elif form_alphabetic.validate_on_submit():
        tournament_player = TournamentPlayer.query.get(form_alphabetic.player_name.data)

    else:
        tournament_player = None

    return render_template(
        "tournament/tournament_player_stats.html",
        title=tournament.name,
        tournament=tournament,
        form=form,
        form_alphabetic=form_alphabetic,
        tournament_player=tournament_player,
        surface=tournament.surface.class_name
    )


def build_player_choices(players):
    return [(-1, _("choose_player"))] + [
        (p.id, p.get_full_name_surname_first())
        for p in players
        if (p.player is None or p.player.last_name.lower() != "bye")
    ]
