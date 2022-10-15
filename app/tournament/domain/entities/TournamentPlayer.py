class TournamentPlayer:
    def __init__(self, tournament_player):
        self.tournament_player = tournament_player

    def get_player(self):
        return self.tournament_player.player

    def is_bye(self):
        if not self.get_player():
            return False
        return self.get_player().last_name == "Bye"

