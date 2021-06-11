import logging
import pickle
from typing import List

import torch
from torch import nn

import src
from apps.fog.FederatedParticipants import DS_with_federation, DS_no_federation
from apps.fog.components import FederatedFogTrainerProvider, SendModelToClient, FederatedFogTrainer, plotter, \
    build_federated_participants
from libs.model.cv.cnn import CNN_OriginalFedAvg
from libs.model.cv.resnet import resnet56
from libs.model.linear.net import Net
from src.data import data_loader
from src.data.data_container import DataContainer
from src.federated.components import metrics, client_selectors, aggregators, params, trainers
from libs.model.linear.lr import LogisticRegression
from src.data.data_provider import PickleDataProvider
from src.federated import subscribers
from src.data.data_generator import DataGenerator
from src.federated.components.trainers import CPUTrainer
from src.federated.events import FederatedEventPlug
from src.federated.federated import Events
from src.federated.federated import FederatedLearning
from src.federated.protocols import TrainerParams
from src.federated.components.trainer_manager import TrainerManager, SeqTrainerManager, SharedTrainerProvider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('main')

# data_file = '../../datasets/pickles/mnist10k.pkl'

logger.info('Generating Data --Started')

# data_file = '../../datasets/pickles/signs_1c_5000mn_6000mx.pkl'
# dg = DataGenerator(PickleDataProvider('https://www.dropbox.com/s/nd25svv30chttln/mnist.zip?dl=1'))
# # dg = DataContainer(x[0:100], y[0:100]).as_tensor()
# client_data = dg.distribute_size(1, 4000, 4000)
# # dg.describe()
# logger.info('Generating Data --Ended')

# dg = src.data.data_generator.load(data_file)
# dg = DataContainer(x[0:100], y[0:100]).as_tensor()
client_data = data_loader.signs_1c_4000min_4000max()
# dg.describe()
logger.info('Generating Data --Ended')

rounds = 1
fog_providers = 1


def create_model():
    # lr = LogisticRegression(28 * 28, 10)
    lr = resnet56(43, 1, 32)
    # lr.load_state_dict(torch.load('../../datasets/models/mnist_start'))
    # lr.eval()
    return lr


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
            # initial_model=lambda: resnet56(43, 1, 32),
            initial_model=create_model,
            num_rounds=rounds,
            desired_accuracy=0.99,
            train_ratio=0.8,
        )
        federated.add_subscriber(subscribers.FederatedLogger([Events.ET_TRAINER_SELECTED, Events.ET_ROUND_FINISHED]))
        federated.add_subscriber(subscribers.Timer([subscribers.Timer.ROUND]))
        federated.add_subscriber(subscribers.FedPlot())
        federated.add_subscriber(SendModelToClient(trainer_provider))
        federated.init()
        fogs.append(federated)
    federated_fog_accuracy = [0] * rounds
    for _ in range(rounds):
        for fog in fogs:
            fog: FederatedLearning
            fog.one_round()
            federated_fog_accuracy[_] += fog.context.history[_]['acc'] / fog_providers * 100
    return federated_fog_accuracy, fogs[0].context.model


data = []
our_approach = get_accuracy(DS_with_federation)
data.append([our_approach[0], 'Our Approach'])
torch.save(our_approach[1].state_dict(), '../../datasets/models/signs_start')
# data.append([get_accuracy(DS_no_federation), 'Static Approach'])
plotter(data, 'Round', 'Average Model Accuracy (%)', rounds)
