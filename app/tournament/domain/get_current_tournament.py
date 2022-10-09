from ...models import Tournament, TournamentStatus


def get_current_tournament():
    return Tournament.query.filter(
        Tournament.status < TournamentStatus.FINISHED
    ).order_by(
        Tournament.started_at.desc()
    ).first()
