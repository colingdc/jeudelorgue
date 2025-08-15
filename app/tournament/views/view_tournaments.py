from flask import render_template, request, current_app
from flask_login import login_required

from .. import bp
from ...models import Tournament


@bp.route("/all")
@login_required
def view_tournaments():
    title = "Tournois"
    page = request.args.get("page", 1, type=int)
    pagination = (Tournament.query.order_by(Tournament.started_at.desc())
                  .filter(Tournament.deleted_at == None)
                  .order_by(Tournament.started_at.desc())
                  .paginate(page=page, per_page=current_app.config["TOURNAMENTS_PER_PAGE"], error_out=False))
    return render_template(
        "tournament/view_tournaments.html",
        title=title,
        pagination=pagination
    ) 

