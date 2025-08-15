from flask import redirect, render_template, request, url_for

from .. import bp
from ..forms import CreateCategoryForm
from ...decorators import manager_required
from ...lang import WORDINGS
from ...models import db, TournamentCategory
from ...utils import display_info_toast


@bp.route("/create", methods=["GET", "POST"])
@manager_required
def create_category():
    title = "Créer une catégorie de tournois"
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
        display_info_toast(WORDINGS.TOURNAMENT.TOURNAMENT_CATEGORY_CREATED.format(category.name))
        return redirect(url_for(".create_category"))
    else:
        return render_template(
            "tournament_category/create_category.html",
            title=title,
            form=form
        ) 
