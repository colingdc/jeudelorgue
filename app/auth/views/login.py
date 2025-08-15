from flask import render_template, redirect, request, session, url_for
from flask_login import login_user, current_user

from .. import bp
from ..forms import LoginForm
from ...lang import WORDINGS
from ...models import User
from ...utils import display_success_toast, display_info_toast


@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    # Redirect user to homepage if they are already authenticated
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for("main.index"))

    # If form was submitted via a POST request
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        # If the credentials are incorrect, render the login page with an error message
        if user is None:
            form.username.errors.append(WORDINGS.AUTH.INCORRECT_CREDENTIALS)
            form.password.errors.append("")
            return render_template(
                "auth/login.html",
                form=form,
                title=WORDINGS.AUTH.LOGIN
            )

        is_password_correct = user.verify_password(form.password.data)
        if not is_password_correct:
            form.username.errors.append(WORDINGS.AUTH.INCORRECT_CREDENTIALS)
            form.password.errors.append("")
            return render_template(
                "auth/login.html",
                form=form,
                title=WORDINGS.AUTH.LOGIN
            )

        # Otherwise log the user in
        login_user(
            user,
            remember=form.remember_me.data
        )
        session["signed"] = True
        session["username"] = user.username
        display_success_toast(WORDINGS.AUTH.LOGIN_SUCCESSFUL)

        if user.is_old_account and not user.confirmed:
            display_info_toast(WORDINGS.AUTH.OLD_ACCOUNT_PASSWORD_CHANGE)
            return redirect(url_for(".change_password"))

        # Redirect the user to the page he initially wanted to access
        if session.get("next"):
            next_page = session.get("next")
            session.pop("next")
            return redirect(next_page)
        else:
            return redirect(url_for("main.index"))

    session["next"] = request.args.get("next")
    return render_template(
        "auth/login.html",
        form=form,
        title=WORDINGS.AUTH.LOGIN
    ) 
