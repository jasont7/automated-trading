import yfinance as yf
import pandas as pd

# tickers = pd.read_csv('data/tickers_small_plus.csv', squeeze=True).dropna().to_list()

# df = yf.download(tickers, '2020-01-01', '2024-01-01', auto_adjust=True)
# df.to_csv('data/data_small_plus_2020-2024.csv')

df = pd.read_csv('data/data_small_plus_2020-2024.csv', header=[0, 1], index_col=0, parse_dates=True)

for attribute in df.columns.levels[0]:
    df[attribute].to_csv(f'data/{attribute}.csv')
