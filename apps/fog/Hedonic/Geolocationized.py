class Geolocationized:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_distance(self, geo2):
        geo2: Geolocationized

        return (((self.x - geo2.x) ** 2) + ((self.y - geo2.y) ** 2)) ** 0.5
