import logging

import torch
from torch import nn

import libs.model.collection
from libs.model.cv.cnn import CNN_OriginalFedAvg
from libs.model.linear.lr import LogisticRegression
from src import tools
from src.data.data_generator import load
from src.data.data_provider import LocalMnistDataProvider, PickleDataProvider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('main')

dit = {1: 'a', 2: 'b', 3: 'c'}
print([dit[i] for i in [1, 3]])
exit()


class CarsModel(torch.nn.Module):
    def __init__(self, only_digits=True):
        super(CarsModel, self).__init__()
        self.only_digits = only_digits
        self.conv2d_1 = torch.nn.Conv2d(1, 32, kernel_size=5, padding=2)
        self.max_pooling = nn.MaxPool2d(2, stride=2)
        self.conv2d_2 = torch.nn.Conv2d(32, 64, kernel_size=5, padding=2)
        self.flatten = nn.Flatten()
        self.linear_1 = nn.Linear(65536, 512)
        self.linear_2 = nn.Linear(512, 10)
        self.relu = nn.ReLU()
        self.softmax = nn.Softmax(dim=1)

    def forward(self, x):
        x = x.view(-1, 128, 128)
        x = torch.unsqueeze(x, 1)
        x = self.conv2d_1(x)
        x = self.max_pooling(x)
        x = self.conv2d_2(x)
        x = self.max_pooling(x)
        x = self.flatten(x)
        x = self.linear_1(x)
        x = self.relu(x)
        x = self.linear_2(x)
        x = self.softmax(x)
        return x


logger.info('Generating Data --Started')
dp = PickleDataProvider('../../datasets/pickles/cars.pkl').collect()
logger.info('Shuffling')
dp = dp.shuffle().as_tensor()
logger.info('Splitting')
x, y = dp.split(0.8)
logger.info('Generating Data --Ended')

lr = LogisticRegression(128 * 128, 9)
tools.train(lr, x.batch(256), 20, 0.1)
acc, loss = tools.infer(lr, y.batch(64))
print(acc)
print(loss)