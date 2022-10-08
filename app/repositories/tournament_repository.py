from ..models import Tournament


class TournamentRepository:
    @staticmethod
    def get_by_id(tournament_id):
        return Tournament.query.get_or_404(tournament_id)
