from flask import render_template

from .. import bp
from ...lang import WORDINGS


@bp.route("/faq")
def faq():
    return render_template(
        "main/faq.html",
        title=WORDINGS.MAIN.FAQ
    ) 
