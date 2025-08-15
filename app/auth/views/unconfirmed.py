from flask import render_template, redirect, url_for
from flask_login import current_user

from .. import bp


@bp.route("/unconfirmed")
def unconfirmed():
    if current_user.confirmed:
        return redirect(url_for("main.index"))
    return render_template("auth/unconfirmed.html")
