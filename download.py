import yfinance as yf
import pandas as pd

# tickers = pd.read_csv('data/tickers/tickers_small_plus.csv', squeeze=True).dropna().to_list()
tickers = pd.read_csv('data/tickers/tickers_mid_plus.csv', squeeze=True).dropna().to_list()
# tickers = pd.read_csv('data/tickers/tickers_large_plus.csv', squeeze=True).dropna().to_list()
# tickers = [
#     'AGL', 'MPW', 'VYGR', 'ALLO', 'CPRX', 'TBPH', 'PUYI', 'DYN', 'AMBI', 'DH', 'BLND',
#     'BGNE', 'EXAI', 'BALY', 'IMCR', 'ZH', 'BFST', 'LBPH', 'ERAS', 'VMEO',
# ]

df = yf.download(tickers, '2020-01-01', '2024-01-01', auto_adjust=True)

for attribute in df.columns.levels[0]:
    df[attribute].to_csv(f'data/2020-2024_mid_plus/{attribute}.csv')
