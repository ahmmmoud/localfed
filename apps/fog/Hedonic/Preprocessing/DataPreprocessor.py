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
# file_path = __location__ + "\grid_1.tcl"
file_path = __lfile_path = "/home/ahmmmoud/projects/def-zdziong/ahmmmoud/localfed/apps/fog/Hedonic/Preprocessing" + "/grid_1.tcl"
file_line_start = 0

def extract_users(time, max_users):
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
        if key == time:
            result = g
    objectified_users = []
    for r in result:
        objectified_users.append(User(r[2], r[3]))
    if max_users <= 0:
        return result, objectified_users
    else:
        return result[0:max_users], objectified_users[0:max_users]

def create_providers(users):
    providers = []
    i1 = i2 = 0
    xx = [0, 500, 1000, 1500]
    users_index = 0
    index = 0
    for x in range(4):
        i2 = 0
        for i in range(3):
            users_objectified = []
            for u in users[users_index]:
                users_objectified.append(u)
            all_resources = 10
            required_resources = [9,10,11]
            providers.append(
                Provider(FogServer(xx[i1], xx[i2], 500), FogServer(10000, 10000, 10000), users_objectified, 0.2, all_resources, required_resources[index%3]))
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


def get_providers_users(time, max_users, display_data=False):
    users, objectified = extract_users(time, max_users)
    objectified = sorted(objectified, key=takeSecond)
    objectified_partitioned_users = partition(objectified, 12)
    providers = create_providers(objectified_partitioned_users)
    if display_data:
        Presenter.display(providers)
    return providers, len(users)
