from types import SimpleNamespace

from .player import wordings as player_wordings
from .tournament import wordings as tournament_wordings

WORDINGS = SimpleNamespace(
    PLAYER=player_wordings,
    TOURNAMENT=tournament_wordings,
)
