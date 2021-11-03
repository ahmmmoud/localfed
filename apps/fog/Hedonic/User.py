from apps.fog.Hedonic.Geolocationized import Geolocationized


class User(Geolocationized):
    static_id = 0

    def __init__(self, x, y):
        super().__init__(x, y)
        self.id = User.static_id
        User.static_id += 1

    def __str__(self):
        return str(self.id)

    def __repr__(self):
        return str(self)
