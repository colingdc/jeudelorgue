# -*- coding: utf-8 -*-

from flask import render_template, redirect, request, flash, url_for, current_app
import datetime
from . import bp
from .forms import CreateCategoryForm, EditCategoryForm
from .. import db
from ..decorators import manager_required
from ..models import TournamentCategory


@bp.route("/create", methods=["GET", "POST"])
@manager_required
def create_category():
    title = u"Créer une catégorie de tournois"
    form = CreateCategoryForm(request.form)
    if form.validate_on_submit():
        category = TournamentCategory(
            name=form.name.data,
            number_rounds=form.number_rounds.data,
            maximal_score=form.maximal_score.data,
            minimal_score=form.minimal_score.data
        )
        db.session.add(category)
        db.session.commit()
        flash(u"La catégorie de tournois {} a été créée".format(category.name), "info")
        return redirect(url_for(".create_category"))
    else:
        return render_template(
            "tournament_category/create_category.html",
            title=title,
            form=form
        )


@bp.route("/<category_id>/edit", methods=["GET", "POST"])
@manager_required
def edit_category(category_id):
    category = TournamentCategory.query.get_or_404(category_id)
    title = category.name
    form = EditCategoryForm(request.form)
    if request.method == "GET":
        form.name.data = category.name
        form.number_rounds.data = category.number_rounds
        form.maximal_score.data = category.maximal_score
        form.minimal_score.data = category.minimal_score
    if form.validate_on_submit():
        category.name = form.name.data
        category.number_rounds = form.number_rounds.data
        category.maximal_score = form.maximal_score.data
        category.minimal_score = form.minimal_score.data
        db.session.add(category)
        db.session.commit()
        flash(u"La catégorie de tournois {} a été mise à jour".format(category.name), "info")
        return redirect(
            url_for(
                ".edit_category",
                category_id=category_id
            )
        )
    else:
        return render_template(
            "tournament_category/edit_category.html",
            title=title,
            form=form,
            category=category
        )


@bp.route("/<category_id>")
@manager_required
def view_category(category_id):
    category = TournamentCategory.query.get_or_404(category_id)
    title = category.name
    return render_template(
        "tournament_category/view_category.html",
        title=title,
        category=category
    )


@bp.route("/<category_id>/delete")
@manager_required
def delete_category(category_id):
    category = TournamentCategory.query.get_or_404(category_id)
    category.deleted_at = datetime.datetime.now()
    db.session.add(category)
    db.session.commit()
    flash(u"La catégorie {} a été supprimé".format(category.name), "info")
    return redirect(url_for(".view_categories"))


@bp.route("/all")
@manager_required
def view_categories():
    title = "Catégories de tournois"
    page = request.args.get("page", 1, type=int)
    pagination = (TournamentCategory.query.order_by(TournamentCategory.name)
                  .filter(TournamentCategory.deleted_at.is_(None))
                  .paginate(page, per_page=current_app.config["CATEGORIES_PER_PAGE"], error_out=False))
    return render_template(
        "tournament_category/view_categories.html",
        title=title,
        pagination=pagination
    )
