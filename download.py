import yfinance as yf
import pandas as pd

# tickers = pd.read_csv('data/tickers_small_plus.csv', squeeze=True).dropna().to_list()
tickers = pd.read_csv('data/tickers_large_plus.csv', squeeze=True).dropna().to_list()
# tickers = [
#     'AGL',
#     'MPW',
#     'VYGR',
#     'ALLO',
#     'CPRX',
#     'TBPH',
#     'PUYI',
#     'DYN',
#     'AMBI',
#     'DH',
#     'BLND',
#     'BGNE',
#     'EXAI',
#     'BALY',
#     'IMCR',
#     'ZH',
#     'BFST',
#     'LBPH',
#     'ERAS',
#     'VMEO',
# ]

df = yf.download(tickers, '2020-01-01', '2024-01-01', auto_adjust=True)
# df.to_csv('data/temp.csv')

# df = pd.read_csv('data/temp.csv', header=[0, 1], index_col=0, parse_dates=True)

for attribute in df.columns.levels[0]:
    df[attribute].to_csv(f'data/data_2020-2024_large/{attribute}.csv')
