from flask import render_template, redirect, url_for, current_app
from flask_login import current_user

from .. import bp
from ..forms import ContactForm
from ...email import send_email
from ...lang import WORDINGS
from ...utils import display_info_toast


@bp.route("/contact", methods=['GET', 'POST'])
def contact():
    title = "Contact"
    form = ContactForm()
    if form.validate_on_submit():
        message = form.message.data
        if current_user and hasattr(current_user, "username"):
            sender = current_user.username
        else:
            sender = "un utilisateur non connecté"
        send_email(
            to=current_app.config["ADMIN_JDL"],
            subject="Nouveau message de la part de {}".format(sender),
            template="email/contact",
            message=message,
            email=form.email.data,
            user=current_user
        )
        display_info_toast(WORDINGS.MAIN.MESSAGE_SENT)
        return redirect(url_for(".contact"))

    return render_template(
        "main/contact.html",
        form=form,
        title=title
    ) 
