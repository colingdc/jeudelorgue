from flask import redirect, render_template, url_for
from flask_login import current_user

from .. import bp
from ...lang import WORDINGS


@bp.route("/")
def landing():
    if current_user.is_authenticated:
        return redirect(url_for(".index"))
    return render_template(
        "main/homepage.html",
        title=WORDINGS.MAIN.HOMEPAGE
    ) 
