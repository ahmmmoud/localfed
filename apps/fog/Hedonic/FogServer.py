from apps.fog.Hedonic import User
from apps.fog.Hedonic.Geolocationized import Geolocationized


class FogServer(Geolocationized):
    static_id = 0

    def __init__(self, x, y, radius=100):
        super().__init__(x, y)
        self.id = FogServer.static_id
        self.radius = radius
        FogServer.static_id += 1
        pass

    def get_users_in_range(self, users):
        res = []
        for u in users:
            u: User
            if self.get_distance(u) <= self.radius:
                res.append(u)
        return res
