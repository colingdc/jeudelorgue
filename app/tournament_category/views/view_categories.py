from flask import render_template, request, current_app

from .. import bp
from ...decorators import manager_required
from ...lang import WORDINGS
from ...models import TournamentCategory


@bp.route("/all")
@manager_required
def view_categories():
    page = request.args.get("page", 1, type=int)
    pagination = (TournamentCategory.query.order_by(TournamentCategory.name)
                  .filter(TournamentCategory.deleted_at.is_(None))
                  .paginate(page=page, per_page=current_app.config["CATEGORIES_PER_PAGE"], error_out=False))
    return render_template(
        "tournament_category/view_categories.html",
        title=WORDINGS.TOURNAMENT.TOURNAMENT_CATEGORIES,
        pagination=pagination
    ) 
