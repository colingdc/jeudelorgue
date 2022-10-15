from ...models import db


def edit_tournament(tournament, form):
    tournament.name = form.name.data
    tournament.started_at = form.start_date.data
    tournament.surface_id = form.surface.data
    tournament.tournament_topic_url = form.tournament_topic_url.data
    tournament.jeudelorgue_topic_url = form.jeudelorgue_topic_url.data

    db.session.add(tournament)
    db.session.commit()
