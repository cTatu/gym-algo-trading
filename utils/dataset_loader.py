from os import stat
from typing import Iterable
import pandas as pd
import re
from utils.logger import Logger

class DatasetLoader():

    @staticmethod
    def load_dfs(filenames: Iterable[str]) -> Iterable[pd.DataFrame]:
        dfs = []
        for file in filenames:
            if file.endswith('.h5'):
                dfs.append(DatasetLoader.load_hdf(file))
            elif file.endswith('.csv'):
                dfs.append(DatasetLoader.load_csv(file))
        return [df for df in dfs if df is not None]


    @staticmethod
    def load_hdf(filename: str) -> pd.DataFrame:
        matches = re.findall(r'[\/|\\]([a-zA-Z]+)_', filename)
        if matches == []:
            Logger().warning(f'Skipping "{filename}", no Key found')
        else:
            return pd.read_hdf(filename, key=matches[-1])

    @staticmethod
    def load_csv(filename: str) -> pd.DataFrame:
        return pd.read_csv(filename, index_col=0)