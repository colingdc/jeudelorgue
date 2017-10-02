# -*- coding: utf-8 -*-

from flask import render_template, redirect, request, session, flash, url_for
from flask_login import login_user, logout_user, current_user, login_required

from . import auth
from .forms import LoginForm, SignupForm
from ..models import User
from ..models import db, bcrypt
from ..texts import CONFIRMATION_MAIL_SENT, LOGIN_SUCCESSFUL, CONFIRMATION_MAIL_RESENT
from ..texts import INCORRECT_CREDENTIALS, USERNAME_ALREADY_TAKEN, EMAIL_ALREADY_TAKEN
from ..texts import ACCOUNT_CONFIRMED, INVALID_CONFIRMATION_TOKEN
from ..email import send_email


@auth.route("/signup", methods = ["GET", "POST"])
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
                       'email/confirm', user = user, token = token)
            flash(CONFIRMATION_MAIL_SENT)
            session.pop("signed", None)
            session.pop("username", None)
            logout_user()
            return redirect(url_for("auth.login"))
    else:
        return render_template("auth/signup.html", form = form, title = title)


@auth.route("/login", methods = ["GET", "POST"])
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

        is_password_correct = bcrypt.check_password_hash(user.password, form.password.data)
        if not is_password_correct:
            form.username.errors.append(INCORRECT_CREDENTIALS)
            form.password.errors.append("")
            return render_template("auth/login.html", form = form, title = title)

        # Otherwise log the user in
        login_user(user, remember = form.remember_me.data)
        session["signed"] = True
        session["username"] = user.username
        flash(LOGIN_SUCCESSFUL)

        # Redirect the user to the page he initially wanted to access
        if session.get("next"):
            next_page = session.get("next")
            session.pop("next")
            return redirect(next_page)
        else:
            return redirect(url_for("main.index"))

    session["next"] = request.args.get("next")
    return render_template("auth/login.html", form = form, title = title)


@auth.route("/logout")
def logout():
    session.pop("signed", None)
    session.pop("username", None)
    logout_user()
    return redirect(url_for("main.landing"))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect('main.index')
    return render_template('auth/unconfirmed.html')


@auth.route("/confirm/<token>")
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash(ACCOUNT_CONFIRMED)
    else:
        flash(INVALID_CONFIRMATION_TOKEN)
    return redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, "Confirmation de votre adresse mail",
               'email/confirm', user = current_user, token = token)
    flash(CONFIRMATION_MAIL_RESENT)
    return redirect(url_for('main.index'))
