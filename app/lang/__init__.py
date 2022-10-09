from types import SimpleNamespace

from .auth import wordings as auth_wordings
from .common import wordings as common_wordings
from .main import wordings as main_wordings
from .player import wordings as player_wordings
from .ranking import wordings as ranking_wordings
from .tournament import wordings as tournament_wordings

WORDINGS = SimpleNamespace(
    AUTH=auth_wordings,
    COMMON=common_wordings,
    MAIN=main_wordings,
    PLAYER=player_wordings,
    RANKING=ranking_wordings,
    TOURNAMENT=tournament_wordings,
)
