from flask import render_template, request
from flask_babel import _

from .. import bp
from .. import domain
from .. import routing
from ..forms import CreateTournamentForm
from ...decorators import manager_required
from ...utils import display_info_toast


@bp.route("/create", methods=["GET", "POST"])
@manager_required
def create_tournament():
    form = CreateTournamentForm(request.form)
    form.category.choices = domain.get_categories()
    form.surface.choices = domain.get_surfaces()

    if form.validate_on_submit():
        tournament = domain.create_tournament(form)
        display_info_toast(_("tournament_created {name}").format(name=form.name.data))
        return routing.redirect_to_view_tournament(tournament.id)
    else:
        return render_template(
            "tournament/create_tournament.html",
            title=_("create_tournament"),
            form=form
        ) 

