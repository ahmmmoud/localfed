import json
import os

import src
from src import manifest
import logging

from src.data.data_generator import DataGenerator
from src.data.data_provider import PickleDataProvider

urls = json.load(open(manifest.DATA_PATH + "urls.json", 'r'))

logger = logging.getLogger('data_loader')


def mnist_10shards_100c_400min_400max():
    file_path = manifest.DATA_PATH + "mnist_10shards_100c_400mn_400mx.pkl"
    if os.path.exists(file_path):
        logger.info('distributed data file exists, loading...')
        return src.data.data_generator.load(file_path).get_distributed_data()
    else:
        logger.info('distributed data file does not exists, distributing...')
        data_provider = PickleDataProvider(urls['mnist'])
        data_generator = DataGenerator(data_provider)
        client_data = data_generator.distribute_shards(100, 10, 400, 400)
        data_generator.save(file_path)
        return client_data


def mnist_2shards_100c_600min_600max():
    file_path = manifest.DATA_PATH + "mnist_2shards_100c_600mn_600mx.pkl"
    if os.path.exists(file_path):
        logger.info('distributed data file exists, loading...')
        return src.data.data_generator.load(file_path).get_distributed_data()
    else:
        logger.info('distributed data file does not exists, distributing...')
        data_provider = PickleDataProvider(urls['mnist'])
        data_generator = DataGenerator(data_provider)
        client_data = data_generator.distribute_shards(100, 2, 600, 600)
        data_generator.save(file_path)
        return client_data


def femnist_2shards_100c_600min_600max():
    file_path = manifest.DATA_PATH + "femnist_2shards_100c_600mn_600mx.pkl"
    if os.path.exists(file_path):
        logger.info(f'distributed data file exists, loading from {file_path}...')
        return src.data.data_generator.load(file_path).get_distributed_data()
    else:
        logger.info(f'distributed data file does not exists, distributing into {file_path}...')
        data_provider = PickleDataProvider(urls['femnist'])
        data_generator = DataGenerator(data_provider)
        client_data = data_generator.distribute_shards(100, 2, 600, 600)
        data_generator.save(file_path)
        return client_data


def kdd_100c_400min_400max():
    file_path = manifest.DATA_PATH + "kdd_100c_400min_400max.pkl"
    if os.path.exists(file_path):
        logger.info(f'distributed data file exists, loading from {file_path}...')
        return src.data.data_generator.load(file_path).get_distributed_data()
    else:
        logger.info(f'distributed data file does not exists, distributing into {file_path}...')
        data_provider = PickleDataProvider(urls['kdd'])
        data_generator = DataGenerator(data_provider)
        client_data = data_generator.distribute_size(100, 400, 400)
        data_generator.save(file_path)
        return client_data
