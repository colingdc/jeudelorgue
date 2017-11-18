# -*- coding: utf-8 -*-

from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required
from . import bp
from ..decorators import admin_required
from ..models import User, Role
from .. import db
from ..texts import PROFILE_UPDATED
from .forms import EditProfileAdminForm


@bp.route("/")
def landing():
    title = "Accueil"

    return render_template("main/homepage.html", title = title)


@bp.route("/index")
def index():
    title = "Accueil"
    return render_template("main/index.html", title = title)


@bp.route("/user/<username>")
def user(username):
    user = User.query.filter_by(username = username).first_or_404()
    title = "Profil de {}".format(username)
    return render_template("main/user.html", title = title, user = user)


@bp.route("/edit-profile/<int:id>", methods = ['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    title = "Modification de profil"
    user = User.query.get_or_404(id)
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
        return redirect(url_for(".user", username = user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    return render_template("main/edit_profile.html", form = form, user = user, title = title)
