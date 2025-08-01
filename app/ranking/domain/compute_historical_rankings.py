from collections import defaultdict

from dateutil.relativedelta import relativedelta

from ...models import (
    db,
    Participant,
    Ranking,
    Tournament,
    TournamentStatus,
)


def compute_historical_rankings(tournament):
    participations = (
        Participant.query
            .join(Tournament, Tournament.id == Participant.tournament_id)
            .filter(Tournament.deleted_at.is_(None))
            .filter(Tournament.status == TournamentStatus.FINISHED)
            .filter(Tournament.started_at <= tournament.started_at)
            .with_entities(Participant.user_id, Participant.points, Tournament.started_at)
            .all()
    )

    annual_participations = [
        participation for participation in participations
        if participation.started_at > tournament.started_at - relativedelta(years=1, days=-3)
    ]

    year_to_date_participations = [
        participation for participation in participations
        if participation.started_at.year == tournament.started_at.year
    ]

    annual_stats = compute_user_stats(annual_participations)
    year_to_date_stats = compute_user_stats(year_to_date_participations)

    update_rankings(tournament.id, annual_stats, year_to_date_stats)


def compute_user_stats(participations):
    stats_by_user = defaultdict(lambda: {"points": 0, "number_tournaments": 0})

    for participation in participations:
        user_id, points, _ = participation
        stats_by_user[user_id]["user_id"] = user_id
        stats_by_user[user_id]["points"] += points
        stats_by_user[user_id]["number_tournaments"] += 1

    sorted_stats = sorted(stats_by_user.values(), key=lambda x: x["points"], reverse=True)

    for rank, user_stats in enumerate(sorted_stats, start=1):
        user_stats["rank"] = rank

    return {
        stats["user_id"]: stats
        for stats in sorted_stats
    }


def update_rankings(tournament_id, annual_stats, year_to_date_stats):
    all_user_ids = set(annual_stats.keys()) | set(year_to_date_stats.keys())

    for user_id in all_user_ids:
        ranking = get_or_create_ranking(user_id, tournament_id)

        if user_id in annual_stats:
            stats = annual_stats[user_id]
            ranking.annual_points = stats["points"]
            ranking.annual_ranking = stats["rank"]
            ranking.annual_number_tournaments = stats["number_tournaments"]

        if user_id in year_to_date_stats:
            stats = year_to_date_stats[user_id]
            ranking.year_to_date_points = stats["points"]
            ranking.year_to_date_ranking = stats["rank"]
            ranking.year_to_date_number_tournaments = stats["number_tournaments"]

        db.session.add(ranking)

    db.session.commit()


def get_or_create_ranking(user_id, tournament_id):
    ranking = (
        Ranking.query
            .filter(Ranking.tournament_id == tournament_id)
            .filter(Ranking.user_id == user_id)
            .first()
    )

    if ranking:
        return ranking

    return Ranking(user_id=user_id, tournament_id=tournament_id)
