import datetime

from flask_babel import _

from .. import bp
from .. import domain
from .. import routing
from ...decorators import manager_required
from ...models import db
from ...utils import display_info_toast


@bp.route("/<tournament_id>/delete")
@manager_required
def delete_tournament(tournament_id):
    tournament = domain.get_tournament(tournament_id)
    tournament.deleted_at = datetime.datetime.now()
    db.session.add(tournament)
    db.session.commit()
    display_info_toast(_("tournament_deleted {name}").format(name=tournament.name))
    return routing.redirect_to_view_tournaments() 
