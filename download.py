import os
import yfinance as yf
import pandas as pd

tickers = pd.read_csv('data/tickers/tickers_small_plus.csv', squeeze=True).dropna().to_list()
# tickers = pd.read_csv('data/tickers/tickers_mid_plus.csv', squeeze=True).dropna().to_list()
# tickers = pd.read_csv('data/tickers/tickers_large_plus.csv', squeeze=True).dropna().to_list()
# tickers = ['ADM', 'RILY', 'ZLAB', 'GILD', 'CORT', 'XPEV', 'HCM', 'COMM', 'GOTU', 'ASTL']

df = yf.download(tickers, period='2d', auto_adjust=True)

output_dir = 'data/test1'
os.makedirs(output_dir, exist_ok=True)

for attribute in df.columns.levels[0]:
    df[attribute].to_csv(f'{output_dir}/{attribute}.csv')


