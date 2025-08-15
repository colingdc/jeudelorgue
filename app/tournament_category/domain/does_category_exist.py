from app.models import TournamentCategory


def does_category_exist(name):
    return TournamentCategory.query.filter_by(name=name).first() is not None
