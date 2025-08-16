from flask import render_template
from flask_babel import _

from .. import bp


@bp.route("/faq")
def faq():
    return render_template(
        "main/faq.html",
        title=_("faq")
    ) 
