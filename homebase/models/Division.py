class Division:
    division_id: int
    lastUpdated: str

    def __init__(self):
        self.division_id = 0
        self.lastUpdated = ""
    
    def as_tuple(self):
        return (self.lastUpdated, self.division_id)