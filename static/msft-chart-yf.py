import pandas as pd
import pandas_ta as ta
import yfinance as yf
from lightweight_charts import Chart
import numpy as np


if __name__ == '__main__':
    
    chart = Chart()
    symbol = "MSFT"
    msft = yf.Ticker(symbol)
    df = msft.history(period="1y")

    # prepare indicator values
    # sma = df.ta.sma(length=20).to_frame()
    # sma = sma.reset_index()
    # sma = sma.rename(columns={"Date": "time", "SMA_20": "value"})
    # sma = sma.dropna()

    # this library expects lowercase columns for date, open, high, low, close, volume
    df = df.reset_index()
    df.columns = df.columns.str.lower()
    chart.set(df)

    # add sma line
    # line = chart.create_line()    
    # line.set(sma)

    chart.watermark(symbol)
    
    chart.show(block=True)