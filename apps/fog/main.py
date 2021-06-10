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
from src.federated.components import metrics, client_selectors, aggregators, params, trainers
from libs.model.linear.lr import LogisticRegression
from src.data.data_provider import PickleDataProvider
from src.federated import plugins
from src.data.data_generator import DataGenerator
from src.federated.components.trainers import CPUTrainer
from src.federated.events import FederatedEventPlug
from src.federated.federated import Events
from src.federated.federated import FederatedLearning
from src.federated.protocols import TrainerParams
from src.federated.trainer_manager import TrainerManager, SeqTrainerManager, SharedTrainerProvider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('main')

# data_file = '../../datasets/pickles/mnist10k.pkl'

logger.info('Generating Data --Started')

# data_file = '../../datasets/pickles/signs_05per_200c_200mn_500mx.pkl'
dg = DataGenerator(PickleDataProvider('https://www.dropbox.com/s/nd25svv30chttln/mnist.zip?dl=1'))
# # dg = DataContainer(x[0:100], y[0:100]).as_tensor()
client_data = dg.distribute_size(100, 400, 400)
# # dg.describe()
# logger.info('Generating Data --Ended')

# dg = src.data.data_generator.load(data_file)
# dg = DataContainer(x[0:100], y[0:100]).as_tensor()
# client_data = dg.distributed
# dg.describe()
logger.info('Generating Data --Ended')

rounds = 8
fog_providers = 5


def get_accuracy(dataset):
    trainer_provider = FederatedFogTrainerProvider()

    fogs = []

    for fog in range(fog_providers):
        trainer_params = TrainerParams(trainer_class=FederatedFogTrainer, batch_size=10, epochs=50, optimizer='sgd',
                                       criterion='cel', lr=0.1)
        federated = FederatedLearning(
            trainer_manager=SeqTrainerManager(trainer_provider),
            trainer_params=trainer_params,
            aggregator=aggregators.AVGAggregator(),
            metrics=metrics.AccLoss(batch_size=50, criterion=nn.CrossEntropyLoss()),
            client_selector=client_selectors.FederatedFogClients(build_federated_participants(fog, dataset)),
            trainers_data_dict=client_data,
            #initial_model=lambda: resnet56(10, 1, 32),
            initial_model=lambda: LogisticRegression(28 * 28, 10),
            num_rounds=rounds,
            desired_accuracy=0.99,
            train_ratio=0.8,
        )
        federated.plug(plugins.FederatedLogger([Events.ET_TRAINER_SELECTED, Events.ET_ROUND_FINISHED]))
        federated.plug(plugins.FederatedTimer([Events.ET_ROUND_FINISHED]))
        federated.plug(plugins.FedPlot())
        federated.plug(SendModelToClient(trainer_provider))
        federated.init()
        fogs.append(federated)
    federated_fog_accuracy = [0] * rounds
    for _ in range(rounds):
        for fog in fogs:
            fog: FederatedLearning
            fog.one_round()
            federated_fog_accuracy[_] += fog.context.history[_]['acc'] / fog_providers * 100
    return federated_fog_accuracy


data = []
data.append([get_accuracy(DS_with_federation), 'Our Approach'])
# data.append([get_accuracy(DS_no_federation), 'Static Approach'])
plotter(data, [0, rounds, 0, 100], 'Round', 'Average Model Accuracy (%)', rounds)
