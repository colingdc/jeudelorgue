from .update_tournament_maximal_score import update_tournament_maximal_score
from ...models import db, TournamentPlayer


def create_tournament_draw(tournament, matches, form):
    qualifier_count = 0
    for match, p in zip(matches, form.player):
        if p.data["player1_name"] >= 0:
            player_id = p.data["player1_name"]
            qualifier_id = None
        else:
            player_id = None
            qualifier_count += 1
            qualifier_id = qualifier_count
        t1 = TournamentPlayer(
            player_id=player_id,
            seed=p.data["player1_seed"],
            status=p.data["player1_status"],
            position=0,
            qualifier_id=qualifier_id,
            tournament_id=tournament.id
        )
        if p.data["player2_name"] >= 0:
            player_id = p.data["player2_name"]
            qualifier_id = None
        else:
            player_id = None
            qualifier_count += 1
            qualifier_id = qualifier_count
        t2 = TournamentPlayer(
            player_id=player_id,
            seed=p.data["player2_seed"],
            status=p.data["player2_status"],
            position=1,
            qualifier_id=qualifier_id,
            tournament_id=tournament.id
        )

        # Add tournament players
        db.session.add(t1)
        db.session.add(t2)
        db.session.commit()

        # Link these tournament players to the match
        match.tournament_player1_id = t1.id
        match.tournament_player2_id = t2.id
        db.session.add(match)
        db.session.commit()

    update_tournament_maximal_score(tournament)
