import time
import logging

import numpy as np

from src import tools
from src.federated import FederatedEventPlug, Events
import matplotlib.pyplot as plt


class FederatedTimer(FederatedEventPlug):
    def __init__(self, only=None):
        super().__init__(only)
        self.last_tick = 0
        self.first_tick = 0
        self.logging = logging.getLogger("fed_timer")

    def tick(self, name):
        now = time.process_time()
        dif = now - self.last_tick
        self.last_tick = now
        self.logging.debug(f'{name}, elapsed: {dif}s')

    def on_federated_started(self, params):
        self.last_tick = time.process_time()
        self.first_tick = time.process_time()

    def on_federated_ended(self, params):
        self.tick('fed end')
        dif = time.process_time() - self.first_tick
        self.logging.debug(f"federated total time: {dif}s")

    def on_init(self, params):
        pass

    def on_training_start(self, params):
        pass

    def on_training_end(self, params):
        self.tick('training')

    def on_aggregation_end(self, params):
        self.tick('aggregation')

    def on_round_end(self, params):
        pass

    def on_round_start(self, params):
        pass

    def on_trainers_selected(self, params):
        self.tick('trainer selection')


class FederatedLogger(FederatedEventPlug):
    def __init__(self, only=None, detailed_selection=False):
        super().__init__(only)
        self.detailed_selection = detailed_selection
        self.trainers_data_dict = None
        self.logger = logging.getLogger('federated')

    def on_federated_started(self, params):
        if self.detailed_selection:
            self.trainers_data_dict = params['trainers_data_dict']
        self.logger.debug('federated learning started')

    def on_federated_ended(self, params):
        self.logger.debug(f'federated learning ended {params}')

    def on_init(self, params):
        self.logger.debug(f'federated learning initialized with initial model {params}')

    def on_training_start(self, params):
        self.logger.debug(f"training started {params}")

    def on_training_end(self, params):
        self.logger.debug(f"training ended {params}")

    def on_aggregation_end(self, params):
        self.logger.debug(f"aggregation ended {params}")

    def on_round_end(self, params):
        self.logger.debug(f"round ended {params}")
        self.logger.debug("----------------------------------------")

    def on_round_start(self, params):
        self.logger.debug(f"round started {params}")

    def force(self) -> []:
        return [Events.ET_FED_START]

    def on_trainers_selected(self, params):
        self.logger.debug(f"selected trainers {params}")
        if self.detailed_selection:
            tools.detail(self.trainers_data_dict, params['trainers_ids'])


class FedPlot(FederatedEventPlug):
    def __init__(self):
        super().__init__()
        self.round_accuracy = []
        self.round_loss = []

    def on_federated_started(self, params):
        pass

    def on_federated_ended(self, params):
        pass

    def on_init(self, params):
        pass

    def on_training_start(self, params):
        pass

    def on_training_end(self, params):
        pass

    def on_aggregation_end(self, params):
        pass

    def on_round_end(self, params):
        self.round_accuracy.append(params['accuracy'])
        self.round_loss.append(params['loss'])
        round_id = params['round']
        if round_id >= 2:
            fig, axs = plt.subplots(2)
            fig.suptitle(f'Accuracy & Loss Round({round_id})')
            axs[0].plot(np.linspace(0, round_id, round_id+1), self.round_accuracy)
            axs[1].plot(np.linspace(0, round_id, round_id+1), self.round_loss)
            plt.show()

    def on_round_start(self, params):
        pass

    def on_trainers_selected(self, params):
        pass
