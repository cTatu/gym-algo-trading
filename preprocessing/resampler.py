from enum import Enum
from preprocessing import Preprocessor
import pandas as pd

class TimeResamplerPreprocessor(Preprocessor):
    def __init__(self, interval : str) -> None:
        self.interval = interval

    def prefix(self) -> str:
        return None

    def _add_change(self, df : pd.DataFrame) -> pd.DataFrame:
        return df.resample(self.interval).agg({'Open': 'first', 
                                 'High': 'max', 
                                 'Low': 'min', 
                                 'Close': 'last'})