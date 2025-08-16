from flask import render_template, redirect, request, url_for
from flask_babel import gettext as _
from flask_login import current_user

from .. import bp
from ..forms import PasswordResetRequestForm
from ...email import send_email
from ...models import User
from ...utils import display_info_toast


@bp.route("/reset", methods=["GET", "POST"])
def reset_password_request():
    if not current_user.is_anonymous:
        return redirect(url_for("main.index"))

    form = PasswordResetRequestForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, "Réinitialisation de votre mot de passe",
                       "email/reset_password",
                       user=user, token=token,
                       next=request.args.get("next"))
            display_info_toast(_("reset_password_email_sent"))
        return redirect(url_for("auth.login"))

    return render_template(
        "auth/reset_password_request.html",
        form=form,
        title=_("password_change")
    )
