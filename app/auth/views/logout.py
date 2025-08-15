from flask import session, redirect, url_for
from flask_login import logout_user

from .. import bp


@bp.route("/logout")
def logout():
    session.pop("signed", None)
    session.pop("username", None)
    logout_user()
    return redirect(url_for("main.landing")) 
