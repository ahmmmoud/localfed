from src.data.data_generator import DataGenerator
from src.data.data_provider import LocalMnistDataProvider, PickleDataProvider


if True:
    print("loading...")
    dg = DataGenerator(PickleDataProvider("../datasets/pickles/signs.pkl"))
    print("distributing...")
    # dg.distribute_shards(num_clients=100, shards_per_client=10, min_size=400, max_size=400, verbose=1)
    dg.distribute_size_redundant(num_clients=300, max_size=3000, min_size=500)
    dg.describe()
    print("saving...")
    dg.save('./pickles/signs_red_300c_500mn_3000mx.pkl')
    print("finished")
