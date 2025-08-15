from flask import render_template, request, current_app

from .. import bp
from ...decorators import manager_required
from ...lang import WORDINGS
from ...models import User


@bp.route("/user/all")
@manager_required
def view_users():
    page = request.args.get("page", 1, type=int)
    pagination = (User.query.order_by(User.username)
                  .filter(User.deleted_at == None)
                  .paginate(page=page, per_page=current_app.config["USERS_PER_PAGE"], error_out=False))
    return render_template(
        "main/view_users.html",
        title=WORDINGS.MAIN.USERS,
        pagination=pagination,
        page_start_index=(page - 1) * current_app.config["USERS_PER_PAGE"]
    ) 
