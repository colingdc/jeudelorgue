from flask import render_template, request, current_app

from .. import bp
from ...decorators import manager_required
from ...lang import WORDINGS
from ...models import Player


@bp.route("/all")
@manager_required
def view_players():
    page = request.args.get("page", 1, type=int)
    pagination = (Player.query.order_by(Player.last_name, Player.first_name)
                  .filter(Player.deleted_at.is_(None))
                  .paginate(page=page, per_page=current_app.config["PLAYERS_PER_PAGE"], error_out=False))

    return render_template(
        "player/view_players.html",
        title=WORDINGS.PLAYER.PLAYERS,
        pagination=pagination
    ) 
