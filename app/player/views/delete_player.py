import datetime

from flask import redirect, url_for
from flask_babel import _

from .. import bp
from ...decorators import manager_required
from ...models import db, Player
from ...utils import display_info_toast


@bp.route("/<player_id>/delete")
@manager_required
def delete_player(player_id):
    player = Player.query.get_or_404(player_id)
    player.deleted_at = datetime.datetime.now()
    db.session.add(player)
    db.session.commit()
    display_info_toast(_("player_deleted {name}").format(name=player.get_full_name()))
    return redirect(url_for(".view_players")) 
