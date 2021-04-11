from abc import ABCMeta, abstractmethod
import pandas as pd

class Preprocessor(metaclass=ABCMeta):

    def process(self, df : pd.DataFrame) -> pd.DataFrame:
        new_df = self._add_change(df.copy(deep=False)).dropna()
        if self.prefix is not None:
            return self.__add_prefix_cols(old_df=df, new_df=new_df)
        return new_df

    def __add_prefix_cols(self, old_df : pd.DataFrame, new_df : pd.DataFrame) -> pd.DataFrame:
        new_cols = set(new_df.columns).difference(set(old_df.columns))
        return new_df.rename(columns={ new_col: f'{self.prefix}.{new_col}' for new_col in new_cols })

    @abstractmethod
    def _add_change(self, df : pd.DataFrame) -> pd.DataFrame:
        pass

    @property
    @abstractmethod
    def prefix(self) -> str:
        pass