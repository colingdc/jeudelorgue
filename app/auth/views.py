# -*- coding: utf-8 -*-

from flask import render_template, redirect, request, session, flash, url_for
from flask_login import login_user, logout_user, current_user, login_required

from . import bp
from .forms import LoginForm, SignupForm, ChangePasswordForm, PasswordResetForm, PasswordResetRequestForm
from ..models import User
from ..models import db
from ..texts import CONFIRMATION_MAIL_SENT, LOGIN_SUCCESSFUL, CONFIRMATION_MAIL_RESENT
from ..texts import INCORRECT_CREDENTIALS, USERNAME_ALREADY_TAKEN, EMAIL_ALREADY_TAKEN
from ..texts import ACCOUNT_CONFIRMED, INVALID_CONFIRMATION_TOKEN
from ..email import send_email


@bp.route("/signup", methods = ["GET", "POST"])
def signup():
    title = "Inscription"
    form = SignupForm(request.form)

    if form.validate_on_submit():
        user_exist = User.query.filter_by(username = form.username.data).first()
        email_exist = User.query.filter_by(email = form.email.data).first()
        if user_exist:
            form.username.errors.append(USERNAME_ALREADY_TAKEN)
        if email_exist:
            form.email.errors.append(EMAIL_ALREADY_TAKEN)
        if user_exist or email_exist:
            return render_template("auth/signup.html", form = form, title = title)
        else:
            user = User(username = form.username.data,
                        email = form.email.data,
                        password = form.password.data)
            db.session.add(user)
            db.session.commit()
            token = user.generate_confirmation_token()
            send_email(user.email, "Confirmation de votre adresse mail",
                       "email/confirm", user = user, token = token)
            flash(CONFIRMATION_MAIL_SENT, "info")
            session.pop("signed", None)
            session.pop("username", None)
            logout_user()
            return redirect(url_for("auth.login"))
    else:
        return render_template("auth/signup.html", form = form, title = title)


@bp.route("/login", methods = ["GET", "POST"])
def login():
    form = LoginForm()
    title = "Connexion"

    # Redirect user to homepage if they are already authenticated
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for("main.index"))

    # If form was submitted via a POST request
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()

        # If the credentials are incorrect, render the login page with an error message
        if user is None:
            form.username.errors.append(INCORRECT_CREDENTIALS)
            form.password.errors.append("")
            return render_template("auth/login.html", form = form, title = title)

        is_password_correct = user.verify_password(form.password.data)
        if not is_password_correct:
            form.username.errors.append(INCORRECT_CREDENTIALS)
            form.password.errors.append("")
            return render_template("auth/login.html", form = form, title = title)

        # Otherwise log the user in
        login_user(user, remember = form.remember_me.data)
        session["signed"] = True
        session["username"] = user.username
        flash(LOGIN_SUCCESSFUL, "success")

        # Redirect the user to the page he initially wanted to access
        if session.get("next"):
            next_page = session.get("next")
            session.pop("next")
            return redirect(next_page)
        else:
            return redirect(url_for("main.index"))

    session["next"] = request.args.get("next")
    return render_template("auth/login.html", form = form, title = title)


@bp.route("/logout")
def logout():
    session.pop("signed", None)
    session.pop("username", None)
    logout_user()
    return redirect(url_for("main.landing"))


@bp.route("/unconfirmed")
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect("main.index")
    return render_template("auth/unconfirmed.html")


@bp.route("/confirm/<token>")
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for("main.index"))
    if current_user.confirm(token):
        flash(ACCOUNT_CONFIRMED, "success")
    else:
        flash(INVALID_CONFIRMATION_TOKEN, "error")
    return redirect(url_for("main.index"))


@bp.route("/confirm")
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, "Confirmation de votre adresse mail",
               "email/confirm", user = current_user, token = token)
    flash(CONFIRMATION_MAIL_RESENT, "info")
    return redirect(url_for("main.index"))


@bp.route("/change-password", methods = ["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash("Votre mot de passe a été mis à jour", "success")
            return redirect(url_for("main.index"))
        else:
            form.old_password.errors.append("Mot de passe incorrect")
    return render_template("auth/change_password.html", form = form)


@bp.route("/reset", methods = ["GET", "POST"])
def reset_password_request():
    if not current_user.is_anonymous:
        return redirect(url_for("main.index"))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, "Réinitialisation de votre mot de passe",
                       "email/reset_password",
                       user = user, token = token,
                       next = request.args.get("next"))
            flash("Un email contenant des instructions pour réinitialiser "
                  "votre mot de passe vous a été envoyé.",
                  "info")
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password_request.html", form = form)


@bp.route("/reset/<token>", methods = ["GET", "POST"])
def reset_password(token):
    if not current_user.is_anonymous:
        return redirect(url_for("main.index"))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user is None:
            return redirect(url_for("main.index"))
        if user.reset_password(token, form.password.data):
            flash("Votre mot de passe a été mis à jour.", "success")
            return redirect(url_for("auth.login"))
        else:
            return redirect(url_for("main.index"))
    return render_template("auth/reset_password.html", form = form, token = token)

