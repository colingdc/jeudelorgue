from flask import redirect, render_template, request, url_for
from flask_babel import gettext as _

from .. import bp
from ..forms import EditCategoryForm
from ...decorators import manager_required
from ...models import db, TournamentCategory
from ...utils import display_info_toast


@bp.route("/<category_id>/edit", methods=["GET", "POST"])
@manager_required
def edit_category(category_id):
    category = TournamentCategory.query.get_or_404(category_id)
    form = EditCategoryForm(request.form)
    if request.method == "GET":
        form.name.data = category.name
        form.number_rounds.data = category.number_rounds
        form.maximal_score.data = category.maximal_score
        form.minimal_score.data = category.minimal_score
    if form.validate_on_submit():
        category.name = form.name.data
        category.maximal_score = form.maximal_score.data
        category.minimal_score = form.minimal_score.data
        db.session.add(category)
        db.session.commit()
        display_info_toast(_("category_updated {name}").format(name=category.name))
        return redirect(
            url_for(
                ".edit_category",
                category_id=category_id
            )
        )
    else:
        return render_template(
            "tournament_category/edit_category.html",
            title=_("tournament_categories"),
            form=form,
            category=category
        ) 
