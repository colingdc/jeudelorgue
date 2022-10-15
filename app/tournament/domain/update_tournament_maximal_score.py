from ...models import db


def update_tournament_maximal_score(tournament):
    tournament.maximal_score = tournament.get_maximal_score()
    db.session.add(tournament)
    db.session.commit()
