from contextlib import suppress

from Federation import Federation
from FogServer import FogServer


class Provider:
    static_id = 0

    def __init__(self, fog_server: FogServer, users, satisfied_participants_rate):
        self.id = Provider.static_id
        Provider.static_id += 1
        self.fog_server: FogServer = fog_server
        self.users = users
        self.satisfied_participants_rate = satisfied_participants_rate
        self.federation = None
        self.neutralize_federation()
        self.history = []

    def get_available_users(self):
        return self.fog_server.get_users_in_range(self.users)

    def get_available_users_by_federation(self):
        providers = self.federation.members
        res = []
        for provider in providers:
            res.extend(provider.fog_server.get_users_in_range(self.users))
        return list(set(res))

    def get_available_users_by_other_federation(self, federation):
        federation: Federation
        providers = federation.members
        res = []
        for provider in providers:
            res.extend(provider.fog_server.get_users_in_range(self.users))
        return list(set(res))

    def get_available_users_by_other_provider(self, provider):
        provider: Provider
        return provider.fog_server.get_users_in_range(self.users)

    def get_explicitly_available_users_by_other_federation(self, federation):
        federation: Federation
        other_federation_access = self.get_available_users_by_other_federation(federation)
        self_federation_access = self.get_available_users_by_federation()
        for u in self_federation_access:
            if u in other_federation_access:
                other_federation_access.remove(u)
        # with suppress(ValueError):
        #     [p2_u.remove(u) for u in p1_u]
        return other_federation_access

    def get_explicitly_available_users_by_other_provider(self, provider):
        provider: Provider
        provider_access = self.get_available_users_by_other_provider(provider)
        self_access = self.get_available_users()
        for u in self_access:
            if u in provider_access:
                provider_access.remove(u)
        # with suppress(ValueError):
        #     [p2_u.remove(u) for u in p1_u]
        return provider_access

    def get_participants_rate(self):
        return len(self.get_available_users()) / len(self.users)

    def get_participants_rate_by_federation(self):
        return len(self.get_available_users_by_federation()) / len(self.users)

    def get_explicitly_participants_rate_by_other_provider(self, provider):
        provider: Provider
        return len(self.get_explicitly_available_users_by_other_provider(provider)) / len(self.users)

    def get_explicitly_participants_rate_by_other_federation(self, federation):
        federation: Federation
        return len(self.get_explicitly_available_users_by_other_federation(federation)) / len(self.users)

    def neutralize_federation(self):
        if self.federation is None:
            return Federation(self)

        if self.federation.get_member_size() == 1:
            raise Exception(str(self) + " already neutralized")
        else:
            return Federation(self)

    def join_federation(self, federation):
        federation.add_member(self)

    def deviate_from_federation(self):
        self.federation.remove_member(self)

    def __str__(self):
        return "Provider " + str(self.id) + "(" + str(self.federation.id) + ")"

    def __repr__(self):
        return str(self)

    def move_to_satisfactory_federation(self, federations):
        if self.get_participants_rate() >= self.satisfied_participants_rate:
            if len(self.federation.members) == 1:
                return False
            self.neutralize_federation()
            return False

        max_rate = 0
        max_fed = None
        for fed in federations:
            fed_rate = self.get_explicitly_participants_rate_by_other_federation(fed)
            if max_rate < fed_rate:
                max_rate = fed_rate
                max_fed = fed

        if max_rate == 0:
            return False

        if max_fed == self.federation:
            # print('didnt change')
            return False

        if self.is_fed_from_history(max_fed):
            # print('history...', self.id)
            return False
        self.add_fed_to_history(max_fed)
        # print(max_rate, max_fed)
        self.deviate_from_federation()
        self.join_federation(max_fed)
        return True

    def add_fed_to_history(self, fed):
        fed_to_history = []
        for m in fed.members:
            fed_to_history.append(m)
        self.history.append(fed_to_history)

    def is_fed_from_history(self, fed: Federation):
        for history in self.history:
            if len(history) == len(fed.members):
                is_history = True
                for history_provider in history:
                    if history_provider not in fed.members:
                        is_history = False
                if is_history:
                    return True
        return False
