from flask import abort, render_template, redirect, request, session, url_for
from flask_babel import gettext as _
from flask_login import logout_user

from .. import bp
from ..forms import SignupForm
from ...email import send_email
from ...models import db, User
from ...utils import display_info_toast


@bp.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm(request.form)

    if form.validate_on_submit():
        if form.anti_bot.data:
            abort(403)

        user_exist = User.query.filter_by(username=form.username.data).first()
        email_exist = User.query.filter_by(email=form.email.data).first()
        if user_exist:
            form.username.errors.append(_("username_already_taken"))
        if email_exist:
            form.email.errors.append(_("email_already_taken"))
        if user_exist or email_exist:
            return render_template(
                "auth/signup.html",
                form=form,
                title=_("registration")
            )
        else:
            user = User(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data
            )
            db.session.add(user)
            db.session.commit()
            token = user.generate_confirmation_token()
            send_email(
                user.email,
                "Confirmation de votre adresse mail",
                "email/confirm",
                user=user,
                token=token
            )

            display_info_toast(_("confirmation_mail_sent"))
            session.pop("signed", None)
            session.pop("username", None)
            logout_user()
            return redirect(url_for("auth.login"))
    else:
        return render_template(
            "auth/signup.html",
            form=form,
            title=_("registration")
        )
