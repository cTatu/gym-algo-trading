from typing import List
import pandas as pd
from glob import glob
import re

class StockDataFrame():
    def __init__(self, df : pd.DataFrame, window_size : int = 2) -> None:
        self.df = df
        self.window_size = window_size
        self.current_index = window_size

    @staticmethod
    def load_all_from_folder(folder_path) -> list:
        all_files : List[str] = glob(f'{folder_path}/*')

        dfs : List[StockDataFrame] = []
        for file in all_files:
            if file.endswith('.h5'):
                matches = re.findall(r'[\/|\\]([a-zA-Z]+)_', file)
                if matches == []:
                    print(f'No Key found for dataset "{file}"')
                else:
                    dfs.append(StockDataFrame(pd.read_hdf(file, key=matches[-1])))
            elif file.endswith('.csv'):
                dfs.append(StockDataFrame(pd.read_csv(file, index_col=0)))

        return dfs

    @property
    def max_price(self) -> float:
        return self.df['High'].max()

    @property
    def state_shape(self) -> tuple:
        return (self.window_size, self.df.shape[1])

    def next(self) -> tuple:
        end = False

        if self.current_index == len(self.df):
            end = True

        state = self.df.iloc[self.current_index - self.window_size:self.current_index].values
        return state, end

    def reset(self):
        self.current_index = self.window_size - 1