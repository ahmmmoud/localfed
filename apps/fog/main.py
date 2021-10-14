import sys
from os.path import dirname

# sys.path.append(dirname(__file__) + '../../../')
sys.path.append('/home/ahmmmoud/projects/def-zdziong/ahmmmoud/localfed/')

from datetime import datetime
import logging
import torch
from torch import nn

from apps.fog.components import FederatedFogTrainerProvider, SendModelToClient, FederatedFogTrainer, plotter, \
    build_federated_participants
from apps.fog.Hedonic.Game import get_federated_participants
from libs.model.cv.resnet import resnet56
from src.data.data_loader import preload
from src.federated import subscribers
from src.federated.components import metrics, client_selectors, aggregators
from src.federated.components.trainer_manager import SeqTrainerManager
from src.federated.federated import Events
from src.federated.federated import FederatedLearning
from src.federated.protocols import TrainerParams
from src.federated.subscribers import Timer

rounds = 2
fog_providers = 1
CLIENTS = 200
LABELS = 30
DATA_PER_CLIENT = 400
DATASET = f'signs_{LABELS}shards_{CLIENTS}c_{DATA_PER_CLIENT}min_{DATA_PER_CLIENT}max'
# print(DATASET)
DISPLAY_OUR_METHOD = 1
DISPLAY_OTHER_METHOD = 0
DISPLAY_NO_FED_METHOD = 0

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('main')

logger.info('Generating Data --Started')
client_data = preload(DATASET, 'signs',
                      lambda dg: dg.distribute_shards(CLIENTS, LABELS, DATA_PER_CLIENT, DATA_PER_CLIENT))
logger.info('Generating Data --Ended')


def create_model():
    # lr = LogisticRegression(28 * 28, 10)
    lr = resnet56(43, 1, 32)
    lr.load_state_dict(torch.load('../../datasets/models/signs_start_20shards_1c_1000min_1000max'))
    # lr.eval()
    return lr


now = datetime.now()
current_dt = now.strftime("_%m-%d-%Y_%H-%M-%S")


def get_accuracy(dataset, approach):
    trainer_provider = FederatedFogTrainerProvider()

    fogs = []

    for fog in range(fog_providers):
        trainer_params = TrainerParams(trainer_class=FederatedFogTrainer, batch_size=10, epochs=20, optimizer='sgd',
                                       criterion='cel', lr=0.1)
        federated = FederatedLearning(
            trainer_manager=SeqTrainerManager(trainer_provider),
            trainer_config=trainer_params,
            aggregator=aggregators.AVGAggregator(),
            metrics=metrics.AccLoss(batch_size=10, criterion=nn.CrossEntropyLoss()),
            client_selector=client_selectors.FederatedFogClients(build_federated_participants(fog, dataset), CLIENTS),
            trainers_data_dict=client_data,
            initial_model=create_model,
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
    federated_fog_loss = [0] * rounds
    for _ in range(rounds):
        for fog in fogs:
            fog: FederatedLearning
            fog.one_round()
            federated_fog_accuracy[_] += fog.context.history[_]['acc'] / fog_providers * 100
            federated_fog_loss[_] += fog.context.history[_]['loss'] / fog_providers
        print(_, federated_fog_accuracy, federated_fog_loss)
        torch.save(fogs[0].context.model.state_dict(),
                   '../../datasets/models/signs_start_20shards_1c_1000min_1000max_trained_' + DATASET + "_"
                   + approach + current_dt + "_" + str(_))
    return federated_fog_accuracy, federated_fog_loss, fogs[0].context.model


data_acc = list()
data_loss = list()

if DISPLAY_OUR_METHOD == 1:
    our_approach = get_accuracy(get_federated_participants(30, 31 + rounds, 0), "ours")
    torch.save(our_approach[2].state_dict(),
               '../../datasets/models/signs_start_20shards_1c_1000min_1000max_trained_' + DATASET + "_ours" + current_dt)
    data_acc.append([our_approach[0], 'Our Approach'])
    data_loss.append([our_approach[1], 'Our Approach'])

if DISPLAY_OTHER_METHOD == 1:
    other_approach = get_accuracy(get_federated_participants(30, 31 + rounds, 1), "static")
    torch.save(other_approach[2].state_dict(),
               '../../datasets/models/signs_start_20shards_1c_1000min_1000max_trained_' + DATASET + "_static" + current_dt)
    data_acc.append([other_approach[0], 'Static Approach'])
    data_loss.append([other_approach[1], 'Static Approach'])

if DISPLAY_NO_FED_METHOD == 1:
    nofed_approach = get_accuracy(get_federated_participants(30, 31 + rounds, 2), "nofed")
    torch.save(nofed_approach[2].state_dict(),
               '../../datasets/models/signs_start_20shards_1c_1000min_1000max_trained_' + DATASET + "_nofed" + current_dt)
    data_acc.append([nofed_approach[0], 'No Federation Approach'])
    data_loss.append([nofed_approach[1], 'No Federation Approach'])

print(data_acc)
plotter(data_acc, [0, rounds, 0, 100], 'Round', 'Average Model Accuracy (%)', rounds)
print(data_loss)
plotter(data_loss, [0, rounds, 0, 100], 'Round', 'Average Model Loss', rounds)
