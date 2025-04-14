# -*- coding: utf-8 -*-

from flask import abort, render_template, flash, redirect, url_for, request
from flask import current_app
from flask_login import login_required, current_user

from . import bp
from .forms import EditProfileAdminForm, ContactForm
from .. import db
from ..decorators import admin_required, manager_required
from ..email import send_email
from ..models import User, Role, Tournament, Participant, TournamentStatus, Ranking
from ..texts import PROFILE_UPDATED


@bp.route("/")
def landing():
    title = "Accueil"
    if current_user.is_authenticated:
      return redirect(url_for(".index"))
    return render_template("main/homepage.html", title = title)


@bp.route("/index")
def index():
    title = "Accueil"
    tournaments = Tournament.get_recent_tournaments(20)
    current_tournament = Tournament.get_current_tournament()
    latest_tournament = Tournament.get_latest_finished_tournament()
    race_ranking = Ranking.get_historical_race_ranking(latest_tournament.id).limit(20)
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

    rankings = Ranking.generate_chart(user_id)

    series = [{"name": "Classement annuel",
               "data": [{"x": int(t.started_at.strftime("%s")) * 1000,
                         "y": t.annual_ranking or "null",
                         "tournament_name": t.name}
                        for t in rankings]},
              {"name": "Classement Race",
               "data": [{"x": int(t.started_at.strftime("%s")) * 1000,
                         "y": t.year_to_date_ranking or "null",
                         "tournament_name": t.name}
                        for t in rankings]}]

    return render_template("main/view_user.html", title = title, user = user, series = series,
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
                           pagination = pagination, page_start_index = (page - 1) * current_app.config["USERS_PER_PAGE"])

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
                           pagination = pagination, page_start_index = (page - 1) * current_app.config["USERS_PER_PAGE"])


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
def contact():
    title = "Contact"
    form = ContactForm()
    if form.validate_on_submit():
        if form.anti_bot.data:
            abort(403)

        message = form.message.data
        if current_user and hasattr(current_user, "username"):
            sender = current_user.username
        else:
            sender = "un utilisateur non connecté"
        send_email(to = current_app.config["ADMIN_JDL"],
                   subject = "Nouveau message de la part de {}".format(sender),
                   template = "email/contact",
                   message = message,
                   email = form.email.data,
                   user = current_user)
        flash(u"Votre message a bien été envoyé.", "info")
        return redirect(url_for(".contact"))

    return render_template("main/contact.html", form = form, title = title)


@bp.route("/test")
def test(chartID = 'chart_ID', chart_type = 'bar', chart_height = 350):
  chart = {"renderTo": chartID, "type": chart_type, "height": chart_height,}
  series = [{"name": 'Label1', "data": [1,2,3]}, {"name": 'Label2', "data": [4, 5, 6]}]
  title = {"text": 'My Title'}
  xAxis = {"categories": ['xAxis Data1', 'xAxis Data2', 'xAxis Data3']}
  yAxis = {"title": {"text": 'yAxis Label'}}
  return render_template('main/test.html', chartID=chartID, chart=chart, series=series, title=title, xAxis=xAxis, yAxis=yAxis)
