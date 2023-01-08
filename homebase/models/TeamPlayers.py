class TeamPlayers:
    player_id: int
    team_id: int

    def __init__(self) -> None:
        self.team_id = 0
        self.division_id = 0

    def as_tuple(self):
        return (self.player_id, self.team_id)
