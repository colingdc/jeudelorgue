from flask_login import login_required

from .. import bp
from .. import domain
from .. import routing


@bp.route("/current")
@login_required
def current_tournament():
    tournament = domain.get_current_tournament()
    if tournament:
        return routing.redirect_to_view_tournament(tournament.id)
    else:
        return routing.redirect_to_view_tournaments() 

