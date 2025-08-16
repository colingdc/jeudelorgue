from flask import render_template

from .. import bp


@bp.route("/contact", methods=['GET'])
def contact():
    return render_template(
        "main/contact.html",
        title="Contact"
    ) 
