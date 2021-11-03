import os
import pickle
import sys
from os.path import dirname
# sys.path.append(dirname(__file__) + '../../../')
sys.path.append('/home/ahmmmoud/projects/def-zdziong/ahmmmoud/localfed/')

# from libs.model.linear.lr import LogisticRegression
from src.apis.rw import IODict
from src.data.data_distributor import LabelDistributor
from src.federated.subscribers.logger import FederatedLogger
from src.federated.subscribers.resumable import Resumable
from src.federated.subscribers.sqlite_logger import SQLiteLogger
from src.federated.subscribers.timer import Timer


from datetime import datetime
import logging
import torch
from torch import nn
from apps.fog.components import FederatedFogTrainerProvider, SendModelToClient, FederatedFogTrainer, plotter, \
    build_federated_participants, FederatedFogClients
from apps.fog.Hedonic.Game import get_federated_participants
from libs.model.cv.resnet import resnet56
from src.data.data_loader import preload
from src.federated.components import metrics, aggregators
from src.federated.components.trainer_manager import SeqTrainerManager
from src.federated.federated import Events
from src.federated.federated import FederatedLearning
from src.federated.protocols import TrainerParams

rounds = 50
fog_providers = 12
CLIENTS = 50
LABELS = 42
DATA_PER_CLIENT = 4000
DATASET = 'signs'
DISPLAY_OUR_METHOD = 1
DISPLAY_OTHER_METHOD = 0
DISPLAY_NO_FED_METHOD = 0

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('main')

logger.info('Generating Data --Started')

if os.path.exists('train.pkl'):
    logger.info("loading data")
    train = pickle.load(open('train.pkl', 'rb'))
    # test = pickle.load(open('test.pkl', 'rb'))
else:
    logger.info("distributing data data")
    distributor = LabelDistributor(CLIENTS, LABELS, DATA_PER_CLIENT, DATA_PER_CLIENT)
    dataset = preload(DATASET)
    # dataset, _ = dataset.shuffle(47).split(0.05)
    train = dataset.shuffle(47).as_tensor()
    # train, test = dataset.shuffle(47).split(0.8)
    # test = test.as_tensor()
    # train = train.as_tensor()
    train = distributor.distribute(train)
    pickle.dump(train, open('train.pkl', 'wb'))
    # pickle.dump(test, open('test.pkl', 'wb'))
logger.info('Generating Data --Ended')


def create_model():
    # lr = LogisticRegression(28 * 28, 10)
    lr = resnet56(43, 1, 32)
    lr.load_state_dict(torch.load('../../datasets/models/boost_sign'))
    # lr.eval()
    return lr


now = datetime.now()
current_dt = now.strftime("_%m-%d-%Y_%H-%M-%S")


def get_accuracy(qos_vehicles_per_provider):
    trainer_provider = FederatedFogTrainerProvider()

    fogs = []

    for fog in range(fog_providers):
        trainer_params = TrainerParams(trainer_class=FederatedFogTrainer, batch_size=20, epochs=10, optimizer='sgd',
                                       criterion='cel', lr=0.01)
        federated = FederatedLearning(
            trainer_manager=SeqTrainerManager(trainer_provider),
            trainer_config=trainer_params,
            aggregator=aggregators.AVGAggregator(),
            metrics=metrics.AccLoss(batch_size=10, criterion=nn.CrossEntropyLoss()),
            client_selector=FederatedFogClients(build_federated_participants(fog, qos_vehicles_per_provider), CLIENTS),
            trainers_data_dict=train,
            initial_model=create_model,
            num_rounds=rounds,
            desired_accuracy=0.99,
            train_ratio=0.8,
            accepted_accuracy_margin=0.05,
            # test_data=test,
            zero_client_exception=False
        )
        federated.add_subscriber(FederatedLogger([Events.ET_TRAINER_SELECTED, Events.ET_ROUND_FINISHED]))
        federated.add_subscriber(Timer([Timer.ROUND]))
        federated.add_subscriber(SendModelToClient(trainer_provider))
        federated.add_subscriber(Resumable(IODict(f'./resumable/cache{fog}.cs'), save_ratio=1))
        federated.add_subscriber(SQLiteLogger(str(fog)))
        federated.init()
        fogs.append(federated)
    federated_fog_accuracy = [0] * rounds
    federated_fog_loss = [0] * rounds
    for _ in range(rounds):
        for fog in fogs:
            fog: FederatedLearning
            fog.one_round()
            federated_fog_accuracy[_] += fog.context.history[_]['acc'] / fog_providers
            federated_fog_loss[_] += fog.context.history[_]['loss'] / fog_providers
        print(_, federated_fog_accuracy, federated_fog_loss)
    return federated_fog_accuracy, federated_fog_loss, fogs[0].context.model


data_acc = list()
data_loss = list()

if DISPLAY_OUR_METHOD == 1:
    our_approach = get_accuracy(get_federated_participants(30, 31 + rounds, CLIENTS, 0))
    data_acc.append([our_approach[0], 'Our Approach'])
    data_loss.append([our_approach[1], 'Our Approach'])

if DISPLAY_OTHER_METHOD == 1:
    other_approach = get_accuracy(get_federated_participants(30, 31 + rounds, CLIENTS, 1))
    data_acc.append([other_approach[0], 'Static Approach'])
    data_loss.append([other_approach[1], 'Static Approach'])

if DISPLAY_NO_FED_METHOD == 1:
    nofed_approach = get_accuracy(get_federated_participants(30, 31 + rounds, CLIENTS, 2))
    data_acc.append([nofed_approach[0], 'No Federation Approach'])
    data_loss.append([nofed_approach[1], 'No Federation Approach'])
    # torch.save(nofed_approach[2].state_dict(), '../../datasets/models/boost_sign')



print(data_acc)
plotter(data_acc, [0, rounds, 0, 1], 'Round', 'Average Test Accuracy', rounds)
print(data_loss)
plotter(data_loss, [0, rounds, 0, 100], 'Round', 'Average Model Loss', rounds)
