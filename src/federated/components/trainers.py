from typing import Tuple, Dict

import torch
from torch import nn
from src.data.data_container import DataContainer
from src.federated.federated import FederatedLearning
from src.federated.protocols import Trainer, TrainerParams


class TorchTrainer(Trainer):
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    def train(self, model: nn.Module, train_data: DataContainer, context: FederatedLearning.Context,
              config: TrainerParams) -> Tuple[any, int]:
        model.to(self.device)
        model.train()
        optimizer = config.get_optimizer()(model)
        criterion = config.get_criterion()

        epoch_loss = []
        for epoch in range(config.epochs):
            # logging.info(epoch)
            batch_loss = []
            for batch_idx, (x, labels) in enumerate(train_data.batch(config.batch_size)):
                # logging.info(batch_idx)
                x = x.to(self.device)
                labels = labels.to(self.device)
                optimizer.zero_grad()
                log_probs = model(x)
                loss = criterion(log_probs, labels)
                loss.backward()
                optimizer.step()
                batch_loss.append(loss.item())
            if len(batch_loss) > 0:
                epoch_loss.append(sum(batch_loss) / len(batch_loss))

        weights = model.cpu().state_dict()
        return weights, len(train_data)


class CPUTrainer(TorchTrainer):
    def __init__(self):
        super().__init__()
        self.device = 'cpu'


class TorchChunkTrainer(TorchTrainer):
    def train(self, model: nn.Module, train_data: DataContainer, context: FederatedLearning.Context,
              config: TrainerParams) -> Tuple[any, int]:
        round_id = context.round_id
        num_rounds = context.federated.num_rounds
        total_size = len(train_data)
        if total_size <= num_rounds:
            raise Exception(
                f'not enough data to run a chunk trainer, data size: {total_size} - num_rounds: {num_rounds}')
        round_data_size = total_size / num_rounds
        x = train_data.x[int(round_id * round_data_size):int((round_id * round_data_size) + round_data_size)]
        y = train_data.y[int(round_id * round_data_size):int((round_id * round_data_size) + round_data_size)]
        chunk = DataContainer(x, y)
        return super(TorchChunkTrainer, self).train(model, chunk, round_id, config)
