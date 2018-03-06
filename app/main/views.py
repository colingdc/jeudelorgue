# -*- coding: utf-8 -*-

from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from . import bp
from ..decorators import admin_required, manager_required
from ..models import User, Role, Tournament, Participant, TournamentStatus
from .. import db
from ..texts import PROFILE_UPDATED
from .forms import EditProfileAdminForm, ContactForm
from ..email import send_email
from flask import current_app


@bp.route("/")
def landing():
    title = "Accueil"
    return render_template("main/homepage.html", title = title)


@bp.route("/index")
def index():
    title = "Accueil"
    tournaments = Tournament.get_recent_tournaments(10)
    current_tournament = Tournament.get_current_tournament()
    race_ranking = User.query.order_by(User.year_to_date_points.desc()).limit(10)
    return render_template("main/index.html", title = title,
                           tournaments = tournaments,
                           current_tournament = current_tournament,
                           race_ranking = race_ranking)


@bp.route("/user/<user_id>")
@login_required
def view_user(user_id):
    user = User.query.get_or_404(user_id)
    title = "Profil de {}".format(user.username)
    page = request.args.get("page", 1, type = int)
    pagination = (user.participants_sorted()
                  .join(Tournament, Tournament.id == Participant.tournament_id)
                  .filter(Tournament.status == TournamentStatus.FINISHED)
                  .filter(Tournament.deleted_at.is_(None))
                  .order_by(Tournament.started_at.desc())
                  .paginate(page, per_page = current_app.config["TOURNAMENTS_PER_PAGE"], error_out = False))
    return render_template("main/user.html", title = title, user = user,
                           pagination = pagination)


@bp.route("/user/all")
@manager_required
def view_users():
    title = "Utilisateurs"
    page = request.args.get("page", 1, type = int)
    pagination = (User.query.order_by(User.username)
                  .filter(User.deleted_at == None)
                  .paginate(page, per_page = current_app.config["USERS_PER_PAGE"], error_out = False))
    return render_template("main/view_users.html", title = title,
                           pagination = pagination)

@bp.route("/user/validated")
@manager_required
def view_validated_users():
    title = "Utilisateurs"
    page = request.args.get("page", 1, type = int)
    pagination = (User.query.order_by(User.username)
                  .filter(User.deleted_at == None)
                  .filter(User.confirmed)
                  .paginate(page, per_page = current_app.config["USERS_PER_PAGE"], error_out = False))
    return render_template("main/view_users.html", title = title,
                           pagination = pagination)


@bp.route("/faq")
def faq():
    title = "FAQ"
    return render_template("main/faq.html", title = title)


@bp.route("/edit-profile/<int:user_id>", methods = ['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(user_id):
    title = "Modification de profil"
    user = User.query.get_or_404(user_id)
    form = EditProfileAdminForm(user = user)
    if request.method == "GET":
        form.email.data = user.email
        form.username.data = user.username
        form.confirmed.data = user.confirmed
        form.role.data = user.role
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        db.session.add(user)
        flash(PROFILE_UPDATED, "success")
        return redirect(url_for(".view_user", user_id = user.id))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    return render_template("main/edit_profile.html", form = form, user = user, title = title)


@bp.route("/contact", methods = ['GET', 'POST'])
@login_required
def contact():
    title = "Contact"
    form = ContactForm()
    if form.validate_on_submit():
        message = form.message.data
        if current_user:
            sender = current_user.username
        else:
            sender = "un utilisateur non connecté"
        send_email(to = current_app.config["ADMIN_JDL"],
                   subject = "Nouveau message de la part de {}".format(sender),
                   template = "email/contact",
                   message = message,
                   user = current_user)
        flash(u"Votre message a bien été envoyé.", "info")
        return redirect(url_for(".contact"))

    return render_template("main/contact.html", form = form, title = title)
