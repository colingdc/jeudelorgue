from flask import render_template
from flask_babel import gettext as _

from .. import bp


@bp.route("/contact", methods=['GET'])
def contact():
    return render_template(
        "main/contact.html",
        title=_("contact")
    ) 
