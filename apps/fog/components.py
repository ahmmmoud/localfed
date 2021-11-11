import logging
import random
from typing import Tuple, List

from torch import nn

from src import tools
from src.data.data_container import DataContainer
from src.federated.components.trainer_manager import SharedTrainerProvider
from src.federated.components.trainers import TorchChunkTrainer, TorchTrainer
from src.federated.events import FederatedEventPlug
from src.federated.federated import FederatedLearning
from src.federated.protocols import TrainerParams, ClientSelector

logger = logging.getLogger('fog components')


class FederatedFogTrainer(TorchTrainer):
    def __init__(self):
        super().__init__()
        self.last_model_weights = None

    def train(self, model: nn.Module, train_data: DataContainer, context: FederatedLearning.Context,
              config: TrainerParams) -> Tuple[any, int]:
        if self.last_model_weights is not None:
            tools.load(model, self.last_model_weights)
            logger.info('model loaded new data')
        return super(FederatedFogTrainer, self).train(model, train_data, context, config)


class FederatedFogTrainerProvider(SharedTrainerProvider):
    def share_global_weights(self, trainer_id, model_weights):
        self.trainers[trainer_id].last_model_weights = model_weights


class SendModelToClient(FederatedEventPlug):
    def __init__(self, trainer_provider):
        super().__init__()
        self.selected_trainers = []
        self.trainer_provider = trainer_provider

    def on_trainers_selected(self, pps):
        selected_trainers = pps['trainers_ids']
        self.selected_trainers = selected_trainers

    def on_aggregation_end(self, pps):
        weights = pps['global_weights']
        for tid in self.selected_trainers:
            self.trainer_provider.share_global_weights(tid, weights)


def plotter(lines, axis_limit, x_label, y_label, rounds):
    import matplotlib.pyplot as plt
    for d in lines:
        plt.plot(d[0], label=d[1])
    plt.axis(axis_limit)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend()
    plt.grid(True)
    plt.show()


def build_federated_participants(fog_id, dataset):
    res = []
    for round_data in dataset:
        tmp_array = []
        for n in round_data[fog_id]:
            # tmp_array.append(n % 10)
            tmp_array.append(n)
        res.append(tmp_array)
    return res


class FederatedFogClients(ClientSelector):
    def __init__(self, arr, max_client_id):
        self.arr = arr
        self.max_client_id = max_client_id
        # self.add_random_participant = add_random_participant

    def select(self, trainer_ids: List[int], round_id: FederatedLearning.Context) -> List[int]:
        selected_trainers = self.arr[round_id.round_id]
        res = []
        for t in selected_trainers:
            res.append(t % self.max_client_id)
        # if self.add_random_participant:
        #     #Add a random trainer for the sake of not being empty
        #     non_empty_rounds = [x for x in self.arr if len(x) > 0]
        #     if len(non_empty_rounds) == 0:
        #         res.append(0)
        #     else:
        #         r_t = random.choice(non_empty_rounds)
        #         random_trainer = random.choice(r_t)
        #         res.append(random_trainer)

        return res
        # return [0]
        # return range(10)
