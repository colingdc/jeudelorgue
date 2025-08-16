from flask import redirect, url_for
from flask_babel import _
from flask_login import login_required, current_user

from .. import bp
from ...email import send_email
from ...utils import display_info_toast


@bp.route("/confirm")
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(
        current_user.email,
        "Confirmation de votre adresse mail",
        "email/confirm",
        user=current_user,
        token=token
    )
    display_info_toast(_("confirmation_mail_resent"))
    return redirect(url_for("main.index")) 
