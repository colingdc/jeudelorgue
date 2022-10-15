from ...models import db
from .update_tournament_maximal_score import update_tournament_maximal_score


def edit_tournament_draw(tournament, matches, form):
    qualifier_count = 0
    for match, p in zip(matches, form.player):
        if p.data["player1_name"] >= 0:
            player_id = p.data["player1_name"]
            qualifier_id = None
        else:
            player_id = None
            qualifier_count += 1
            qualifier_id = qualifier_count

        t1 = match.tournament_player1
        t1.player_id = player_id
        t1.seed = p.data["player1_seed"]
        t1.status = p.data["player1_status"]
        t1.qualifier_id = qualifier_id

        if p.data["player2_name"] >= 0:
            player_id = p.data["player2_name"]
            qualifier_id = None
        else:
            player_id = None
            qualifier_count += 1
            qualifier_id = qualifier_count

        t2 = match.tournament_player2
        t2.player_id = player_id
        t2.seed = p.data["player2_seed"]
        t2.status = p.data["player2_status"]
        t2.qualifier_id = qualifier_id

        # Add tournament players
        db.session.add(t1)
        db.session.add(t2)
        db.session.commit()

    update_tournament_maximal_score(tournament)
