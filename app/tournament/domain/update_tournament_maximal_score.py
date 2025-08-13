from .entities import TournamentPlayer
from ...models import db


def compute_maximal_score(tournament):
    score_per_round = tournament.get_score_per_round()
    score = 0
    for match in tournament.matches:
        if match.tournament_player1 and TournamentPlayer(match.tournament_player1).is_bye():
            continue
        if match.tournament_player2 and TournamentPlayer(match.tournament_player2).is_bye():
            continue
        match_score = score_per_round[match.round]
        score += match_score
    return score


def update_tournament_maximal_score(tournament):
    tournament.maximal_score = compute_maximal_score(tournament)
    db.session.add(tournament)
    db.session.commit()
