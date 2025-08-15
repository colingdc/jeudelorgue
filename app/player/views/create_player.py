from flask import render_template, redirect, request, url_for

from .. import bp
from ..forms import CreatePlayerForm
from ...decorators import manager_required
from ...lang import WORDINGS
from ...models import db, Player
from ...utils import display_info_toast


@bp.route("/create", methods=["GET", "POST"])
@manager_required
def create_player():
    form = CreatePlayerForm(request.form)
    if form.validate_on_submit():
        player = Player(
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        db.session.add(player)
        db.session.commit()
        display_info_toast(WORDINGS.PLAYER.PLAYER_CREATED.format(player.get_full_name()))
        return redirect(url_for(".create_player"))
    else:
        return render_template(
            "player/create_player.html",
            title=WORDINGS.PLAYER.CREATE_PLAYER,
            form=form
        ) 
