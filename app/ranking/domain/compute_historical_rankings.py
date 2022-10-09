from dateutil.relativedelta import relativedelta
import pandas as pd

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
    )

    participations = participations.filter(Tournament.started_at <= tournament.started_at)
    participations = participations.with_entities(Participant.user_id, Participant.points, Tournament.started_at)

    df = pd.read_sql(participations.statement, participations.session.bind)
    df["number_tournaments"] = 1
    df = df.dropna()

    annual_points = df[df["started_at"] > tournament.started_at - relativedelta(years=1, days=-3)].groupby(
        "user_id").sum().sort_values("points", ascending=False).reset_index()
    annual_points["rank"] = range(1, len(annual_points) + 1)
    year_to_date_points = df[df["started_at"].dt.year == tournament.started_at.year].groupby(
        "user_id").sum().sort_values("points", ascending=False).reset_index()
    year_to_date_points["rank"] = range(1, len(year_to_date_points) + 1)

    print("Computing annual points and rankings")
    for _, row in annual_points.iterrows():
        r = Ranking.query.filter(Ranking.tournament_id == tournament.id).filter(
            Ranking.user_id == row["user_id"]).first()
        if r is None:
            r = Ranking(user_id=row["user_id"], tournament_id=tournament.id)
        r.annual_points = row["points"]
        r.annual_ranking = row["rank"]
        r.annual_number_tournaments = row["number_tournaments"]
        db.session.add(r)

    print("Computing year to date points and rankings")
    for _, row in year_to_date_points.iterrows():
        r = Ranking.query.filter(Ranking.tournament_id == tournament.id).filter(
            Ranking.user_id == row["user_id"]).first()
        if r is None:
            r = Ranking(user_id=row["user_id"], tournament_id=tournament.id)
        r.year_to_date_points = row["points"]
        r.year_to_date_ranking = row["rank"]
        r.year_to_date_number_tournaments = row["number_tournaments"]
        db.session.add(r)

    db.session.commit()
