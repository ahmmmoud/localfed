from src.data.data_generator import DataGenerator
from src.data.data_provider import LocalMnistDataProvider, PickleDataProvider


if True:
    print("loading...")
    dg = DataGenerator(PickleDataProvider("../datasets/pickles/signs.pkl"))
    print("distributing...")
    # dg.distribute_shards(num_clients=100, shards_per_client=10, min_size=400, max_size=400, verbose=1)
    dg.distribute_shards_redundant(num_clients=100, max_size=800, min_size=500, shards_per_client=4, verbose=1)
    dg.describe()
    print("saving...")
    dg.save('./pickles/signs_3shards_100c_500mn_800mx.pkl')
    print("finished")
