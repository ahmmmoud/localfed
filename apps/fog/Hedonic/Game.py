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

def print_stats_number_participants(providers):
    res = 0
    for p in providers:
        res += len(p.get_available_users_by_federation())
    print(res)


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
#formation_type = 0 : our approach
#formation_type = 1 : profit approach (static hedonic game by Anglano)
def get_federated_participants(start_time, end_time, formation_type):
    res = []
    for i in range(start_time, end_time):
        Provider.static_id = 0
        User.static_id = 1
        FogServer.static_id = 0
        Federation.static_id = 0
        providers, total_number_of_users = DataPreprocessor.get_providers_users(i, False)

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
        # print_stats_number_participants(providers)
        # print_stats_feds(providers)
        res.append(get_feds(providers))
    # print(res[0])
    return res

#
# get_federated_participants(30,35,0)
# get_federated_participants(30,35,1)


    # calculate_latency()
# print(latencies_no_fed)
# print(latencies_fed)

# for_avg_single = []
# for_avg_fed = []
# for j in range(0,5):
#     print(j)
#     print(j)
#     print(j)
#     print(j)
#     print(j)
#     print(j)
#     print(j)
#     print(j)
#     participants_rate_single = []
#     participants_rate_fed = []
#     for i in range(20, 220):
#         providers, total_number_of_users = DataPreprocessor.get_providers_users(i, False)
#         print(i)
#         # print_stats(providers)
#         while True:
#             equilibrium = True
#             for p in providers:
#                 federations = [f.federation for f in providers]
#                 federations = list(set(federations))
#                 changed = p.move_to_satisfactory_federation(federations)
#                 if changed:
#                     equilibrium = False
#             if equilibrium:
#                 break
#             # print_stats(providers)
#
#         available_number_of_participants = 0
#         for p in providers:
#             available_number_of_participants += len(p.get_available_users_by_federation())
#         participants_rate_fed.append(available_number_of_participants / total_number_of_users)
#         available_number_of_participants_single = 0
#         for p in providers:
#             available_number_of_participants_single += len(p.get_available_users())
#         participants_rate_single.append(available_number_of_participants_single / total_number_of_users)
#
#     for_avg_single.append(participants_rate_single)
#     for_avg_fed.append(participants_rate_fed)
# print(for_avg_single)
# print(for_avg_fed)
#
# import numpy as NP
# arr_s = NP.array(for_avg_single)
# res_single = arr_s.sum(axis=0)
# print(res_single)
#
# arr_f = NP.array(for_avg_fed)
# res_f = arr_f.sum(axis=0)
# print(res_f)
#
# exit()
#
# print("\n\n\n")
# print("pro #", "\t|\t", "single", "|\t", "federation")
# for p in providers:
#     x = p.get_participants_rate()
#     y = p.get_participants_rate_by_federation()
#     x = '{:.2f}'.format(round(x, 2))
#     y = '{:.2f}'.format(round(y, 2))
#     z1 = p.get_participants_rate() * len(p.users)
#     z2 = p.get_participants_rate_by_federation() * len(p.users)
#     print("pro", providers.index(p), "\t|\t", x, "\t|\t", y, "\t|\t", z1, z2, "\t|\t", p.federation.id)


# p1_fs = FogServer(0, 0, 100)
# p2_fs = FogServer(50, 50, 100)
# p3_fs = FogServer(10000, 10000, 100)
#
# p1_users = [
#     User(1, 1),
#     User(1, 1),
#     User(1, 1),
#     User(1, 1),
#     User(10000, 10000),
#     User(10000, 10000),
#     User(100, 100),
# ]
#
# p2_users = [
#     User(1, 1),
#     User(1, 1),
#     User(1, 1),
#     User(1, 1),
#     User(1, 1),
#     User(1, 1),
#     User(100, 100),
#     User(-60, -60),
#     User(1, 1),
#     User(1, 1),
# ]
# p1_satisfied_availability = 0.9
# p2_satisfied_availability = 0.8
# p3_satisfied_availability = 0.7
#
# p1 = Provider(p1_fs, p1_users, p1_satisfied_availability)
# p2 = Provider(p2_fs, p2_users, p2_satisfied_availability)
# p3 = Provider(p3_fs, [], p3_satisfied_availability)

# print("p1 can see", p1.get_available_users())
# print("only p2 can see", p1.get_explicitly_available_users_by_other_provider(p2))
#
# print("p2 can see", p2.get_available_users())
# print("only p1 can see", p2.get_explicitly_available_users_by_other_provider(p1))
#
# print(p1.get_participants_rate())
# print(p1.get_explicitly_participants_rate_by_other_provider(p2))
#
# print(p2.get_participants_rate())
# print(p2.get_explicitly_participants_rate_by_other_provider(p1))


# x = p1.get_explicitly_participants_rate_by_other_federation(f2)
# print(x)
