# -*- coding: utf-8 -*-

from flask import render_template, redirect, request, flash, url_for, current_app
from flask_login import login_required
from . import bp
from .. import db
from ..models import User


@bp.route("/annual")
@login_required
def annual_ranking():
    title = u"Classement annuel"
    page = request.args.get("page", 1, type = int)
    pagination = (User.query.filter(User.confirmed).order_by(User.annual_points.desc())
                  .paginate(page, per_page = current_app.config["USERS_PER_PAGE"], error_out = False))
    return render_template("ranking/annual_ranking.html", title = title,
                           pagination = pagination)


@bp.route("/race")
@login_required
def race_ranking():
    title = u"Classement Race"
    page = request.args.get("page", 1, type = int)
    pagination = (User.query.filter(User.confirmed).order_by(User.year_to_date_points.desc())
                  .paginate(page, per_page = current_app.config["USERS_PER_PAGE"], error_out = False))
    return render_template("ranking/race_ranking.html", title = title,
                           pagination = pagination)
