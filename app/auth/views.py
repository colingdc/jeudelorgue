# -*- coding: utf-8 -*-

from flask import abort, render_template, redirect, request, session, url_for, current_app
from flask_login import login_user, logout_user, current_user, login_required

from . import bp
from .forms import LoginForm, SignupForm, ChangePasswordForm, PasswordResetForm, PasswordResetRequestForm
from ..email import send_email
from ..lang import WORDINGS
from ..models import db, User
from ..utils import (
    display_error_toast,
    display_info_toast,
    display_success_toast,
)


@bp.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm(request.form)

    if form.validate_on_submit():
        if form.anti_bot.data:
            abort(403)

        user_exist = User.query.filter_by(username=form.username.data).first()
        email_exist = User.query.filter_by(email=form.email.data).first()
        if user_exist:
            form.username.errors.append(WORDINGS.AUTH.USERNAME_ALREADY_TAKEN)
        if email_exist:
            form.email.errors.append(WORDINGS.AUTH.EMAIL_ALREADY_TAKEN)
        if user_exist or email_exist:
            return render_template(
                "auth/signup.html",
                form=form,
                title=WORDINGS.AUTH.REGISTRATION
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

            display_info_toast(WORDINGS.AUTH.CONFIRMATION_MAIL_SENT)
            session.pop("signed", None)
            session.pop("username", None)
            logout_user()
            return redirect(url_for("auth.login"))
    else:
        return render_template(
            "auth/signup.html",
            form=form,
            title=WORDINGS.AUTH.REGISTRATION
        )


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


@bp.route("/logout")
def logout():
    session.pop("signed", None)
    session.pop("username", None)
    logout_user()
    return redirect(url_for("main.landing"))


@bp.route("/unconfirmed")
def unconfirmed():
    if current_user.confirmed:
        return redirect(url_for("main.index"))
    return render_template("auth/unconfirmed.html")


@bp.route("/confirm/<token>")
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for("main.index"))
    if current_user.confirm(token):
        display_success_toast(WORDINGS.AUTH.ACCOUNT_CONFIRMED)
    else:
        display_error_toast(WORDINGS.AUTH.INVALID_CONFIRMATION_TOKEN)
    return redirect(url_for("main.index"))


@bp.route("/confirm")
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(
        current_user.email,
        "Confirmation de votre adresse mail",
        "email/confirm",
        user=current_user,
        token=token
    )
    display_info_toast(WORDINGS.AUTH.CONFIRMATION_MAIL_RESENT)
    return redirect(url_for("main.index"))


@bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            if current_user.is_old_account and current_user.confirmed is False:
                current_user.confirmed = True
                send_email(
                    current_app.config.get("ADMIN_JDL"),
                    "Nouvel inscrit au jeu de L'orgue depuis l'ancien site",
                    "email/new_user",
                    user=current_user
                )
            db.session.add(current_user)
            display_success_toast(WORDINGS.AUTH.PASSWORD_UPDATED)
            return redirect(url_for("main.index"))
        else:
            form.old_password.errors.append("Mot de passe incorrect")
    return render_template(
        "auth/change_password.html",
        form=form,
        title=WORDINGS.AUTH.PASSWORD_CHANGE,
        user=current_user
    )


@bp.route("/reset", methods=["GET", "POST"])
def reset_password_request():
    if not current_user.is_anonymous:
        return redirect(url_for("main.index"))

    form = PasswordResetRequestForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, "Réinitialisation de votre mot de passe",
                       "email/reset_password",
                       user=user, token=token,
                       next=request.args.get("next"))
            display_info_toast(WORDINGS.AUTH.RESET_PASSWORD_EMAIL_SENT)
        return redirect(url_for("auth.login"))

    return render_template(
        "auth/reset_password_request.html",
        form=form,
        title=WORDINGS.AUTH.PASSWORD_CHANGE
    )


@bp.route("/reset/<token>", methods=["GET", "POST"])
def reset_password(token):
    if not current_user.is_anonymous:
        return redirect(url_for("main.index"))
    form = PasswordResetForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for("main.index"))
        if user.reset_password(token, form.password.data):
            display_success_toast(WORDINGS.AUTH.PASSWORD_UPDATED)
            return redirect(url_for("auth.login"))
        else:
            return redirect(url_for("main.index"))
    return render_template(
        "auth/reset_password.html",
        form=form,
        token=token,
        title=WORDINGS.AUTH.PASSWORD_CHANGE
    )
