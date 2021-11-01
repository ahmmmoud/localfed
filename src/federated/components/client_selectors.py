import random
from typing import List

from src.federated.federated import FederatedLearning
from src.federated.protocols import ClientSelector


class All(ClientSelector):
    def select(self, trainer_ids: List[int], round_id: int) -> List[int]:
        return trainer_ids


class Random(ClientSelector):
    def __init__(self, num):
        self.num = num

    def select(self, trainer_ids: List[int], round_id: int) -> List[int]:
        select_size = self.num
        if self.num < 1:
            select_size = self.num * len(trainer_ids)
        selected_trainers = random.sample(trainer_ids, select_size)
        return selected_trainers


class FederatedFogClients(ClientSelector):
    def __init__(self, arr, max_client_id):
        self.arr = arr
        self.max_client_id = max_client_id

    def select(self, trainer_ids: List[int], round_id: FederatedLearning.Context) -> List[int]:
        selected_trainers = self.arr[round_id.round_id]
        res = []
        for t in selected_trainers:
            res.append(t % self.max_client_id)
        # return res
        return [0]
