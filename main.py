import glob
import os
import argparse

import pandas as pd
from preprocessing.indicators import IndicatorsPreprocessor, PriceSource
from preprocessing.resampler import TimeResamplerPreprocessor
from preprocessing.datetime_decomposition import DateTimePreprocessor
from preprocessing import Preprocessor
from typing import List

if __name__ == '__main__':
    df = pd.read_hdf('datasets/BCHUSDT_1min.h5', key='BCHUSDT')

    preprocessors : List[Preprocessor] = [
        TimeResamplerPreprocessor('1H'),
        DateTimePreprocessor(),
        IndicatorsPreprocessor().sma(12)
                                .rsi(10, PriceSource.OPEN)
    ]

    for p in preprocessors:
        df = p.process(df)

    print(df.head())