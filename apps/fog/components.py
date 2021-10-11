import logging
from typing import Tuple

from torch import nn

from src import tools
from src.data.data_container import DataContainer
from src.federated.components.trainer_manager import SharedTrainerProvider
from src.federated.components.trainers import TorchChunkTrainer, TorchTrainer
from src.federated.events import FederatedEventPlug
from src.federated.federated import FederatedLearning
from src.federated.protocols import TrainerParams

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
    plt.xticks(range(0, rounds))
    plt.yticks(range(0, 100, 5))
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
