from flask import redirect, render_template, url_for
from flask_babel import gettext as _
from flask_login import current_user

from .. import bp


@bp.route("/")
def landing():
    if current_user.is_authenticated:
        return redirect(url_for(".index"))
    return render_template(
        "main/homepage.html",
        title=_("homepage")
    ) 
