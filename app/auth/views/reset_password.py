from flask import render_template, redirect, url_for
from flask_login import current_user

from .. import bp
from ..forms import PasswordResetForm
from ...lang import WORDINGS
from ...models import User
from ...utils import display_success_toast


@bp.route("/reset/<token>", methods=["GET", "POST"])
def reset_password(token):
    if not current_user.is_anonymous:
        return redirect(url_for("main.index"))
    form = PasswordResetForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for("main.index"))
        if user.reset_password(token, form.password.data):
            display_success_toast(WORDINGS.AUTH.PASSWORD_UPDATED)
            return redirect(url_for("auth.login"))
        else:
            return redirect(url_for("main.index"))
    return render_template(
        "auth/reset_password.html",
        form=form,
        token=token,
        title=WORDINGS.AUTH.PASSWORD_CHANGE
    )
