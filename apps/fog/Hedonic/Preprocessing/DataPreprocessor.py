import itertools
import os
import random
from pprint import pprint

from apps.fog.Hedonic.FogServer import FogServer
from apps.fog.Hedonic.Preprocessing.Presenter import Presenter
from apps.fog.Hedonic.Provider import Provider
from apps.fog.Hedonic.User import User

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
file_path = __location__ + "\grid_1.tcl"
file_line_start = 0


#
# def extract_users(time):
#     result = []
#     with open(file_path) as f:
#         for _ in range(file_line_start):
#             next(f)
#         for line in f:
#             arr = line.split(' ')
#             if len(arr) < 5:
#                 continue
#             arr2 = arr[3].split('(')
#             result.append([int(arr[2].split('.')[0]), int(arr2[1][0:-1]), float(arr[5]), float(arr[6])])
#     key_func = lambda x: x[0]
#
#     for key, group in itertools.groupby(result, key_func):
#         g = list(group)
#         # print(str(key) + " :", str(len(g)))
#
#         if key == time:
#             # import matplotlib.pyplot as plt
#             #
#             # x = [row[2] for row in g]
#             # y = [row[3] for row in g]
#             # plt.scatter(x, y)
#             # plt.show()
#             result = g
#     return result


# def create_providers(users):
#     providers = []
#     i1 = i2 = 0
#     xx = [0, 500, 1000, 1500]
#     users_index = 0
#     for x in range(4):
#         i2 = 0
#         for i in range(3):
#             users_objectified = []
#             for u in users[users_index]:
#                 users_objectified.append(User(u[2], u[3]))
#             providers.append(Provider(FogServer(xx[i1], xx[i2], 200), users_objectified, 0.2))
#             i2 += 1
#             users_index += 1
#         i1 += 1
#     return providers
#
#
# def partition(list_in, n):
#     # random.shuffle(list_in)
#     return [list_in[i::n] for i in range(n)]
#
#
# def get_providers_users(time, display_data=False):
#     users = extract_users(time)
#     # a = len(users)
#     # print(a)
#     # exit()
#     x = partition(users, 12)
#     providers = create_providers(x)
#     if display_data:
#         Presenter.display(providers)
#     return providers

def extract_users(time):
    result = []
    with open(file_path) as f:
        for _ in range(file_line_start):
            next(f)
        for line in f:
            arr = line.split(' ')
            if len(arr) < 5:
                continue
            arr2 = arr[3].split('(')
            result.append([int(arr[2].split('.')[0]), int(arr2[1][0:-1]), float(arr[5]), float(arr[6])])
    key_func = lambda x: x[0]

    for key, group in itertools.groupby(result, key_func):
        g = list(group)
        # print(str(key) + " :", str(len(g)))

        if key == time:
            # import matplotlib.pyplot as plt
            #
            # x = [row[2] for row in g]
            # y = [row[3] for row in g]
            # plt.scatter(x, y)
            # plt.show()
            result = g
    objectified_users = []
    for r in result:
        objectified_users.append(User(r[2], r[3]))
    return result, objectified_users


def create_providers(users):
    providers = []
    i1 = i2 = 0
    xx = [0, 500, 1000, 1500]
    users_index = 0
    for x in range(4):
        i2 = 0
        for i in range(3):
            users_objectified = []
            for u in users[users_index]:
                users_objectified.append(u)
            all_resources = 10
            required_resources = [9,10,11]
            index = 0
            providers.append(
                Provider(FogServer(xx[i1], xx[i2], 500), users_objectified, 0.2, all_resources, required_resources[index%3]))
            index += 1
            i2 += 1
            users_index += 1
        i1 += 1
    return providers


def partition(list_in, n):
    # random.shuffle(list_in)
    return [list_in[i::n] for i in range(n)]


def takeSecond(elem: User):
    return elem.id


def get_providers_users(time, display_data=False):
    users, objectified = extract_users(time)
    objectified = sorted(objectified, key=takeSecond)
    objectified_partitioned_users = partition(objectified, 12)
    providers = create_providers(objectified_partitioned_users)
    if display_data:
        Presenter.display(providers)
    return providers, len(users)
