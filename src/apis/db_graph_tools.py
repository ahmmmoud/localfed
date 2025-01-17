import math
import sqlite3
from collections import defaultdict
from typing import Callable

import numpy as np
from matplotlib import pyplot as plt

from src.apis import utils
from src.apis.fed_sqlite import FedDB


class Graphs:
    def __init__(self, db: FedDB):
        self._db = db

    def db(self):
        return self._db

    def __repr__(self):
        tables = self._db.tables()
        rpr = f'columns: session;config\n'
        for session, config in tables.items():
            rpr += f'{session} \t | \t {config}\n'
        rpr = rpr.rstrip('\n')
        return rpr

    def _as_dict(self, keys, default_value=dict):
        if isinstance(keys, dict):
            return keys
        res = {}
        for key in keys:
            res[key] = default_value(key)
        return res

    def plot(self, configs: list, title='', animated=False):
        """
        Args:
            configs: a array of dictionaries containing session_id: the session id in the database, field: the field name in the table,
                config: the plot configurations, transform: a callable to transform the values to another
            title: the title of the plot
            animated: animate the image (require the original plot to be shown not the one in intellij
        """
        tables = self._db.tables()
        sessions = [(item['session_id'], item['field'], item['config'] if 'config' in item else {},
                     item['transform'] if 'transform' in item else None) for item in configs]
        session_values = {}
        for session_id, field, config, transform in sessions:
            values = self._db.get(session_id, field)
            values = transform(values) if transform else values
            print(values)
            session_values[f'{session_id}_{field}_{str(transform)}'] = values
        if animated:
            pause = 0.05
            session_end = [False] * len(sessions)
            round_id = 0
            session_plot_values = defaultdict(list)
            while False in session_end:
                for session_id, field, config, transform in sessions:
                    try:
                        session_plot_values[f'{session_id}_{field}_{str(transform)}'].append(
                            session_values[f'{session_id}_{field}_{str(transform)}'][round_id])
                        plt.plot(session_plot_values[f'{session_id}_{field}_{str(transform)}'], **config)
                    except IndexError as e:
                        session_end[session_end.index(False)] = True
                plt.pause(pause)
                round_id += 1
        else:
            for session_id, field, config, transform in sessions:
                plt.plot(session_values[f'{session_id}_{field}_{str(transform)}'], **config)
        plt.xlabel('Rounds')
        plt.ylabel('Accuracy')
        plt.title(title)
        plt.legend(loc='lower right')
        plt.show()
