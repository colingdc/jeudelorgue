from flask import render_template, request
from flask_babel import gettext as _

from .. import bp
from .. import domain
from .. import routing
from ..forms import EditTournamentForm
from ...decorators import manager_required
from ...utils import display_info_toast


@bp.route("/<tournament_id>/edit", methods=["GET", "POST"])
@manager_required
def edit_tournament(tournament_id):
    tournament = domain.get_tournament(tournament_id)
    form = EditTournamentForm(request.form)

    form.category.choices = domain.get_categories()
    form.surface.choices = domain.get_surfaces()

    if request.method == "GET":
        form.name.data = tournament.name
        form.category.data = tournament.category_id
        form.surface.data = tournament.surface_id
        form.start_date.data = tournament.started_at
        form.tournament_topic_url.data = tournament.tournament_topic_url
        form.jeudelorgue_topic_url.data = tournament.jeudelorgue_topic_url
    if form.validate_on_submit():
        domain.edit_tournament(tournament, form)
        display_info_toast(_("tournament_updated {name}").format(name=form.name.data))
        return routing.redirect_to_edit_tournament(tournament_id)
    else:
        return render_template(
            "tournament/edit_tournament.html",
            title=tournament.name,
            form=form,
            tournament=tournament,
            surface=tournament.surface.class_name
        ) 

