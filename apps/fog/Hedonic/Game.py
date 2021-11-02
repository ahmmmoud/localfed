# from apps.fog.Hedonic import LatencyPredictor
from apps.fog.Hedonic.FogServer import FogServer
from apps.fog.Hedonic.Preprocessing import DataPreprocessor
from apps.fog.Hedonic.Provider import Provider
from apps.fog.Hedonic.User import User
from apps.fog.Hedonic.Federation import Federation


def print_stats(providers):
    print('[', end='')
    for p in providers:
        p: Provider
        for p2 in p.federation.members:
            print(str(p2.get_available_users_by_federation()) + ",", end='')
    print('],', end='')
    print("\n")


def get_stats_number_participants(providers):
    res = 0
    for p in providers:
        res += len(p.get_available_users_by_federation())
    return res


def get_feds(providers):
    res = []
    for p in providers:
        p: Provider
        res.append(p.get_available_users_by_federation())
    return res


def print_stats_feds(providers):
    for p in providers:
        p: Provider
        print(p.id, str(p.federation.members))
        [print(str(len(a.get_available_users_by_federation())) + ",", end='') for a in p.federation.members]
        print("\n")


# latencies_no_fed = []
# latencies_fed = []
# formation_type = 0 : our approach
# formation_type = 1 : profit approach (static hedonic game by Anglano)
def get_federated_participants(start_time, end_time, max_users, formation_type):
    res = []
    total_participants = 0

    for i in range(start_time, end_time):
        Provider.static_id = 0
        User.static_id = 1
        FogServer.static_id = 0
        Federation.static_id = 0
        providers, total_number_of_users = DataPreprocessor.get_providers_users(i, max_users, False)

        # def calculate_latency():
        #     avg_delay_no_fed = 0
        #     avg_delay_fed = 0
        #     for p in providers:
        #         usrs_no_fed = p.get_available_users()
        #         usrs_fed = p.get_available_users_by_federation()
        #         for u in p.users:
        #             if u not in usrs_no_fed:
        #                 avg_delay_no_fed += 75
        #             else:
        #                 avg_delay_no_fed += 40
        #
        #             if u not in usrs_fed:
        #                 avg_delay_fed += 75
        #             else:
        #                 avg_delay_fed += 40
        #     avg_delay_no_fed /= total_number_of_users
        #     avg_delay_fed /= total_number_of_users
        #     latencies_no_fed.append(avg_delay_no_fed)
        #     latencies_fed.append(avg_delay_fed)

        # print_stats(providers)
        if formation_type != 2:
            while True:
                equilibrium = True
                for p in providers:
                    federations = [f.federation for f in providers]
                    # federations = list(set(federations))
                    if formation_type == 0:
                        changed = p.move_to_satisfactory_federation(federations)
                    elif formation_type == 1:
                        changed = p.move_to_satisfactory_federation_profit(federations)
                    else:
                        raise ValueError('unknown formation type')
                    if changed:
                        equilibrium = False
                if equilibrium:
                    break

            # print_stats(providers)
        # print_stats(providers)
        total_participants += get_stats_number_participants(providers)
        # print_stats_feds(providers)
        res.append(get_feds(providers))
    # print(res[0])
    # print(total_participants)
    return res


def get_participants_rate(start_time, end_time, max_users, formation_type):
    res = []
    for i in range(start_time, end_time):
        Provider.static_id = 0
        User.static_id = 1
        FogServer.static_id = 0
        Federation.static_id = 0
        providers, total_number_of_users = DataPreprocessor.get_providers_users(i, max_users, False)
        if formation_type != 2:
            while True:
                equilibrium = True
                for p in providers:
                    federations = [f.federation for f in providers]
                    if formation_type == 0:
                        changed = p.move_to_satisfactory_federation(federations)
                    elif formation_type == 1:
                        changed = p.move_to_satisfactory_federation_profit(federations)
                    else:
                        raise ValueError('unknown formation type')
                    if changed:
                        equilibrium = False
                if equilibrium:
                    break

        users = sum([len(p.users) for p in providers])
        participants_rate = get_stats_number_participants(providers) / users
        res.append(participants_rate)
    return res


# def get_average_latency(start_time, end_time, max_users, formation_type):
#     res = []
#     for i in range(start_time, end_time):
#         Provider.static_id = 0
#         User.static_id = 1
#         FogServer.static_id = 0
#         Federation.static_id = 0
#         providers, total_number_of_users = DataPreprocessor.get_providers_users(i, max_users, False)
#         if formation_type != 2:
#             while True:
#                 equilibrium = True
#                 for p in providers:
#                     federations = [f.federation for f in providers]
#                     if formation_type == 0:
#                         changed = p.move_to_satisfactory_federation(federations)
#                     elif formation_type == 1:
#                         changed = p.move_to_satisfactory_federation_profit(federations)
#                     else:
#                         raise ValueError('unknown formation type')
#                     if changed:
#                         equilibrium = False
#                 if equilibrium:
#                     break
#
#         latency = 0
#         users = sum([len(p.users) for p in providers])
#         for p in providers:
#             usrs_fed = p.get_available_users_by_federation()
#             for u in p.users:
#                 if u.id in usrs_fed:
#                     latency += LatencyPredictor.predict(p.fog_server, u)[0]
#                 else:
#                     latency += LatencyPredictor.predict(p.cloud_server, u)[0]
#         res.append(latency / users)
#     return res

# #
# s = 0
# a1 = []
# a2 = []
# a3 = []
# for i in range(0, 1):
#     s += 30
#     e = s + 30
#     a1.append(get_participants_rate(s, e, 0))
#     a2.append(get_participants_rate(s, e, 1))
#     a3.append(get_participants_rate(s, e, 2))
# print("part_our = " + str(a1))
# print("part_static = " + str(a2))
# print("part_nofed = " + str(a3))


# s = 0
# a1 = []
# a2 = []
# a3 = []
# for i in range(0, 10):
#     s += 30
#     e = s + 30
#     a1.append(get_average_latency(s, e, 0))
#     a2.append(get_average_latency(s, e, 1))
#     a3.append(get_average_latency(s, e, 2))
# print("latency_our = " + str(a1))
# print("latency_static = " + str(a2))
# print("latency_nofed = " + str(a3))


# a = get_federated_participants(30, 31 + 10, 10, 2)
# print(a)
# a = get_federated_participants(30, 31 + 10, 50, 0)
# print(a)