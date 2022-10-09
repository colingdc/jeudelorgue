from math import log, floor
from ...models import db, Match, Tournament


def create_tournament(form):
    tournament = Tournament(
        name=form.name.data,
        started_at=form.start_date.data,
        category_id=form.category.data,
        surface_id=form.surface.data,
        tournament_topic_url=form.tournament_topic_url.data,
        jeudelorgue_topic_url=form.jeudelorgue_topic_url.data
    )

    db.session.add(tournament)
    db.session.commit()

    create_matches(tournament)

    return tournament


def create_matches(tournament):
    for i in range(1, 2 ** tournament.number_rounds):
        match = Match(
            position=i,
            tournament_id=tournament.id,
            round=floor(log(i) / log(2)) + 1
        )
        db.session.add(match)
    db.session.commit()
