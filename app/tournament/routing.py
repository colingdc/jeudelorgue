from flask import (
    redirect,
    url_for,
)


def redirect_to_view_tournament(tournament_id):
    return redirect(url_for(".view_tournament", tournament_id=tournament_id))


def redirect_to_view_tournament_draw(tournament_id):
    return redirect(url_for(".view_tournament_draw", tournament_id=tournament_id))


def redirect_to_view_tournaments():
    return redirect(url_for(".view_tournaments"))
