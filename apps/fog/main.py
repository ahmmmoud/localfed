import logging
import pickle
from typing import List

from torch import nn

import src
from apps.fog.FederatedParticipants import DS_with_federation, DS_no_federation
from apps.fog.components import FederatedFogTrainerProvider, SendModelToClient, FederatedFogTrainer, plotter, \
    build_federated_participants
from libs.model.cv.cnn import CNN_OriginalFedAvg
from libs.model.cv.resnet import resnet56
from libs.model.linear.net import Net
from src.data.data_container import DataContainer
from src.data.data_loader import preload
from src.federated import subscribers
from src.federated.components import metrics, client_selectors, aggregators, params, trainers
from libs.model.linear.lr import LogisticRegression
from src.data.data_provider import PickleDataProvider
from src.data.data_generator import DataGenerator
from src.federated.components.trainer_manager import SeqTrainerManager
from src.federated.federated import Events
from src.federated.federated import FederatedLearning
from src.federated.protocols import TrainerParams
from src.federated.subscribers import Timer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('main')


logger.info('Generating Data --Started')


# client_data = preload(f'signs_2shards_100c_600min_600max', 'signs', lambda dg: dg.distribute_shards(100, 2, 600, 600))
client_data = preload(f'signs_300shards_1c_2000min_3000max', 'signs', lambda dg: dg.distribute_shards(1, 30, 2000, 3000))
print(client_data)
exit(1)
logger.info('Generating Data --Ended')

rounds = 1
fog_providers = 1


def get_accuracy(dataset):
    trainer_provider = FederatedFogTrainerProvider()

    fogs = []

    for fog in range(fog_providers):
        trainer_params = TrainerParams(trainer_class=FederatedFogTrainer, batch_size=10, epochs=50, optimizer='sgd',
                                       criterion='cel', lr=0.1)
        federated = FederatedLearning(
            trainer_manager=SeqTrainerManager(trainer_provider),
            trainer_config=trainer_params,
            aggregator=aggregators.AVGAggregator(),
            metrics=metrics.AccLoss(batch_size=50, criterion=nn.CrossEntropyLoss()),
            client_selector=client_selectors.FederatedFogClients(build_federated_participants(fog, dataset)),
            trainers_data_dict=client_data,
            initial_model=lambda: resnet56(43, 1, 32),
            # initial_model=lambda: LogisticRegression(28 * 28, 10),
            num_rounds=rounds,
            desired_accuracy=0.99,
            train_ratio=0.8,
        )
        federated.add_subscriber(subscribers.FederatedLogger([Events.ET_TRAINER_SELECTED, Events.ET_ROUND_FINISHED]))
        federated.add_subscriber(subscribers.Timer([Timer.ROUND]))
        # federated.plug(plugins.FedPlot())
        federated.add_subscriber(SendModelToClient(trainer_provider))
        federated.init()
        fogs.append(federated)
    federated_fog_accuracy = [0] * rounds
    for _ in range(rounds):
        for fog in fogs:
            fog: FederatedLearning
            fog.one_round()
            federated_fog_accuracy[_] += fog.context.history[_]['acc'] / fog_providers * 100
    return federated_fog_accuracy


data = list()
data.append([get_accuracy(DS_with_federation), 'Our Approach'])
# data.append([get_accuracy(DS_no_federation), 'Static Approach'])
plotter(data, [0, rounds, 0, 100], 'Round', 'Average Model Accuracy (%)', rounds)
