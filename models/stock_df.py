from preprocessing import Preprocessor
from typing import Iterable, List
import pandas as pd
from glob import glob
from utils.dataset_loader import DatasetLoader
import re

class StockDataFrame():
    def __init__(self, df : pd.DataFrame, window_size : int = 2, preprocessors : Iterable[Preprocessor] = []) -> None:
        self.df = df
        self.window_size = window_size
        self.current_index = window_size + 1
        
        for p in preprocessors:
            self.df = p.process(self.df)

        self.df_array = self.df.values

    @staticmethod
    def load_all_from_folder(folder_path, window_size : int = 2, preprocessors : Iterable[Preprocessor] = []) -> list:
        all_filenames : List[str] = glob(f'{folder_path}/*')

        dfs = DatasetLoader.load_dfs([all_filenames[0]])
        dfs : List[StockDataFrame] = [StockDataFrame(df, window_size, preprocessors) for df in dfs]

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

        state = self.df_array[self.current_index - self.window_size:self.current_index]
        self.current_index += 1
        return state, end

    def reset(self):
        self.current_index = self.window_size + 1