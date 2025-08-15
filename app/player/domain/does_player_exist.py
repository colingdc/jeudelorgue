from app.models import Player


def does_player_exist(first_name, last_name):
    return Player.query.filter_by(first_name=first_name).filter_by(last_name=last_name).first() is not None
