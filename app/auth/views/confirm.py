from flask import redirect, url_for
from flask_login import login_required, current_user

from .. import bp
from ...lang import WORDINGS
from ...utils import display_success_toast, display_error_toast


@bp.route("/confirm/<token>")
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for("main.index"))
    if current_user.confirm(token):
        display_success_toast(WORDINGS.AUTH.ACCOUNT_CONFIRMED)
    else:
        display_error_toast(WORDINGS.AUTH.INVALID_CONFIRMATION_TOKEN)
    return redirect(url_for("main.index")) 
