from flask import redirect, url_for
from flask_babel import gettext as _
from flask_login import login_required, current_user

from .. import bp
from ...utils import display_success_toast, display_error_toast


@bp.route("/confirm/<token>")
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for("main.index"))
    if current_user.confirm(token):
        display_success_toast(_("account_confirmed"))
    else:
        display_error_toast(_("invalid_confirmation_token"))
    return redirect(url_for("main.index")) 
