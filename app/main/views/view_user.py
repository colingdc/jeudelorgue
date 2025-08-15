from flask import render_template, request, current_app
from flask_login import login_required

from .. import bp
from ...lang import WORDINGS
from ...models import User, Participant, Tournament, TournamentStatus, Ranking


@bp.route("/user/<user_id>")
@login_required
def view_user(user_id):
    user = User.query.get_or_404(user_id)
    title = "Profil de {}".format(user.username)
    page = request.args.get("page", 1, type=int)
    pagination = (user.participants_sorted()
                  .join(Tournament, Tournament.id == Participant.tournament_id)
                  .filter(Tournament.status == TournamentStatus.FINISHED)
                  .filter(Tournament.deleted_at.is_(None))
                  .order_by(Tournament.started_at.desc())
                  .paginate(page=page, per_page=current_app.config["TOURNAMENTS_PER_PAGE"], error_out=False))

    rankings = Ranking.generate_chart(user_id)

    series = [
        {
            "name": "Classement annuel",
            "data": [
                {
                    "x": int(t.started_at.strftime("%s")) * 1000,
                    "y": t.annual_ranking or "null",
                    "tournament_name": t.name
                }
                for t in rankings
            ]
        },
        {
            "name": WORDINGS.RANKING.RACE_RANKING,
            "data": [
                {
                    "x": int(t.started_at.strftime("%s")) * 1000,
                    "y": t.year_to_date_ranking or "null",
                    "tournament_name": t.name
                }
                for t in rankings
            ]
        }
    ]

    return render_template(
        "main/view_user.html",
        title=title,
        user=user,
        series=series,
        pagination=pagination
    ) 
