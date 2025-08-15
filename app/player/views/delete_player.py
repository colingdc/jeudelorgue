import datetime

from flask import redirect, url_for

from .. import bp
from ...decorators import manager_required
from ...lang import WORDINGS
from ...models import db, Player
from ...utils import display_info_toast


@bp.route("/<player_id>/delete")
@manager_required
def delete_player(player_id):
    player = Player.query.get_or_404(player_id)
    player.deleted_at = datetime.datetime.now()
    db.session.add(player)
    db.session.commit()
    display_info_toast(WORDINGS.PLAYER.PLAYER_DELETED.format(player.get_full_name()))
    return redirect(url_for(".view_players")) 
