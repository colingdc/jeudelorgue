from flask import render_template, request

from .. import bp
from .. import domain
from .. import routing
from ..forms import CreateTournamentForm
from ...decorators import manager_required
from ...lang import WORDINGS
from ...utils import display_info_toast


@bp.route("/create", methods=["GET", "POST"])
@manager_required
def create_tournament():
    form = CreateTournamentForm(request.form)
    form.category.choices = domain.get_categories()
    form.surface.choices = domain.get_surfaces()

    if form.validate_on_submit():
        tournament = domain.create_tournament(form)
        display_info_toast(WORDINGS.TOURNAMENT.TOURNAMENT_CREATED.format(form.name.data))
        return routing.redirect_to_view_tournament(tournament.id)
    else:
        return render_template(
            "tournament/create_tournament.html",
            title=WORDINGS.TOURNAMENT.CREATE_TOURNAMENT,
            form=form
        ) 

