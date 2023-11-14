class Keyword:
    def __init__(self, id, name, search_volume=None, total_monthly_clicks=None):
        self.id = id
        self.name = name
        self.volume = search_volume
        self.clicks = total_monthly_clicks

    def stats(self):
        print(f"{self.id}, {self.name},{self.volume}, {self.clicks}")