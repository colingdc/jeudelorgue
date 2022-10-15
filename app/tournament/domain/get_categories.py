from ...models import TournamentCategory


def get_categories():
    return [
        (category.id, category.name)
        for category in TournamentCategory.query.order_by(TournamentCategory.name).all()
    ]
