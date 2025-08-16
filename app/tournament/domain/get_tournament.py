from flask import abort

from ...models import Tournament


def get_tournament(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    if tournament.deleted_at:
        abort(404)
    return tournament
