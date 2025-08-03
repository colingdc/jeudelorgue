from collections import Counter

from ...models import db, Match, Forecast


def compute_risk_coefficient_by_participant(tournament):
    number_participants = tournament.participants.count()
    risk_coefficient_by_participant = {participant.id: 0 for participant in tournament.participants}

    tournament_forecasts = (
        db.session.query(Forecast.participant_id, Forecast.winner_id, Match.round, Match.id.label("match_id"))
            .join(Match, Forecast.match_id == Match.id)
            .filter(Match.tournament_id == tournament.id)
            .all()
    )

    forecasts_by_match = {
        match.id: {
            "weight": 2 ** (tournament.number_rounds - match.round),
            "forecasts": []
        }
        for match in tournament.matches
    }
    for forecast in tournament_forecasts:
        forecasts_by_match[forecast.match_id]["forecasts"].append(forecast)

    for match_forecasts in forecasts_by_match.values():
        count_by_winner_id = Counter([x.winner_id for x in match_forecasts["forecasts"]])

        for forecast in match_forecasts["forecasts"]:
            number_different_forecasts = number_participants - count_by_winner_id[forecast.winner_id]
            score = match_forecasts["weight"] * number_different_forecasts
            risk_coefficient_by_participant[forecast.participant_id] += score

    return {participant_id: score / number_participants for participant_id, score in risk_coefficient_by_participant.items()}
