from ...models import db


def compute_maximal_score(tournament):
    score_per_round = tournament.get_score_per_round()
    score = 0
    for match in tournament.matches:
        if match.tournament_player1 and match.tournament_player1.player and match.tournament_player1.player.last_name == "Bye":
            continue
        if match.tournament_player2 and match.tournament_player2.player and match.tournament_player2.player.last_name == "Bye":
            continue
        match_score = score_per_round[match.round]
        score += match_score
    return score


def update_tournament_maximal_score(tournament):
    tournament.maximal_score = compute_maximal_score(tournament)
    db.session.add(tournament)
    db.session.commit()
