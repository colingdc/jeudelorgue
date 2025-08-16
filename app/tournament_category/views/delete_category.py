import datetime

from flask import redirect, url_for
from flask_babel import _

from .. import bp
from ...decorators import manager_required
from ...models import db, TournamentCategory
from ...utils import display_info_toast


@bp.route("/<category_id>/delete")
@manager_required
def delete_category(category_id):
    category = TournamentCategory.query.get_or_404(category_id)
    category.deleted_at = datetime.datetime.now()
    db.session.add(category)
    db.session.commit()
    display_info_toast(_("category_deleted {name}").format(name=category.name))
    return redirect(url_for(".view_categories")) 
