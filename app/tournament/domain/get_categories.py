from ...models import TournamentCategory


def get_categories():
    return TournamentCategory.get_all_categories()
