class Team:
    team_id: int
    division_id: int
    name: str
    abbr: str
    wins_this_season: int
    losses_this_season: int
    win_pct: str
    games_back: str
    last_ten: str
    run_diff: int
    place_in_division: str

    def __init__(self) -> None:
        self.team_id = 0
        self.division_id = 0
        self.name = ""
        self.abbr = ""
        self.wins_this_season = -1
        self.losses_this_season = -1
        self.win_pct = ""
        self.games_back = ""
        self.last_ten = ""
        self.run_diff = -1
        self.place_in_division = ""

    def as_tuple(self):
        return (self.team_id, self.division_id, self.name, self.abbr, self.wins_this_season, self.losses_this_season, self.win_pct, self.games_back, self.last_ten, self.run_diff, self.place_in_division)
