from flask import render_template, redirect, request, url_for

from .. import bp
from ..forms import EditPlayerForm
from ...decorators import manager_required
from ...lang import WORDINGS
from ...models import db, Player
from ...utils import display_info_toast


@bp.route("/<player_id>/edit", methods=["GET", "POST"])
@manager_required
def edit_player(player_id):
    player = Player.query.get_or_404(player_id)
    title = player.get_full_name()
    form = EditPlayerForm(request.form)
    if request.method == "GET":
        form.first_name.data = player.first_name
        form.last_name.data = player.last_name
    if form.validate_on_submit():
        player.first_name = form.first_name.data
        player.last_name = form.last_name.data
        db.session.add(player)
        db.session.commit()
        display_info_toast(WORDINGS.PLAYER.PLAYER_UPDATED.format(player.get_full_name()))
        return redirect(
            url_for(
                ".edit_player",
                player_id=player_id
            )
        )
    else:
        return render_template(
            "player/edit_player.html",
            title=title,
            form=form,
            player=player
        ) 
