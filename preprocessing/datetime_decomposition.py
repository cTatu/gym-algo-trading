
from preprocessing import Preprocessor
import pandas as pd

class DateTimePreprocessor(Preprocessor):
    @property
    def prefix(self) -> str:
        return 'datetime'

    def _add_change(self, df : pd.DataFrame) -> pd.DataFrame:
        df['Year'] = df.index.year
        df['Month'] = df.index.month
        df['Day'] = df.index.day
        df['WeekDay'] = df.index.weekday
        df['Hour'] = df.index.hour
        df['Minute'] = df.index.minute
        return df