import csv
from pprint import pprint
import numpy
import pandas as pd
from math import sin, cos, sqrt, atan2, radians
from sklearn import linear_model
import itertools
import os

from apps.fog.Hedonic.Geolocationized import Geolocationized

latencies = {'Distance': [10, 100, 1000, 50],
             'Latency': [3.79, 5.39, 21.35, 4.5]}

df = pd.DataFrame(latencies, columns=['Distance', 'Latency'])

X = df[['Distance']]
Y = df['Latency']

# with sklearn
regr = linear_model.LinearRegression()
regr.fit(X, Y)


def predict(l1: Geolocationized, l2: Geolocationized):
    lt1 = l1.x
    lg1 = l1.y
    lt2 = l2.x
    lg2 = l2.y
    dist = sqrt((lt2 - lt1) ** 2 + (lg2 - lg1) ** 2)
    late = regr.predict([[dist / 10]])  # in decameters to magnify the map
    return late
