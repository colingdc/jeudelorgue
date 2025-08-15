from flask import render_template, redirect, url_for, current_app
from flask_login import login_required, current_user

from .. import bp
from ..forms import ChangePasswordForm
from ...email import send_email
from ...lang import WORDINGS
from ...models import db
from ...utils import display_success_toast


@bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            if current_user.is_old_account and current_user.confirmed is False:
                current_user.confirmed = True
                send_email(
                    current_app.config.get("ADMIN_JDL"),
                    "Nouvel inscrit au jeu de L'orgue depuis l'ancien site",
                    "email/new_user",
                    user=current_user
                )
            db.session.add(current_user)
            display_success_toast(WORDINGS.AUTH.PASSWORD_UPDATED)
            return redirect(url_for("main.index"))
        else:
            form.old_password.errors.append("Mot de passe incorrect")
    return render_template(
        "auth/change_password.html",
        form=form,
        title=WORDINGS.AUTH.PASSWORD_CHANGE,
        user=current_user
    ) 
