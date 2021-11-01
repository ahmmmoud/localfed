import pickle

from src.apis.rw import IODict

a = pickle.load(open('cache0.cs', 'rb'))
print(a)
aa = a['cached']
f = 1