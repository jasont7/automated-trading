import pandas as pd

# sp500_tickers = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
# sp500_tickers = sp500_tickers.Symbol.to_list()
# for ticker in sp500_tickers:
#     ticker = ticker.replace('.', '-')
#     tickers.add(ticker)

# qqq_tickers = pd.read_html('https://en.m.wikipedia.org/wiki/Nasdaq-100', 
#                            attrs={'id': "constituents"}, index_col='Ticker')[0]
# qqq_tickers = qqq_tickers.index.to_list()
# for ticker in qqq_tickers:
#     ticker = ticker.replace('.', '-')
#     tickers.add(ticker)

def extract_ticker_symbols(file_path):
    ticker_symbols = []

    with open(file_path, 'r') as file:
        next(file)  # skip header line

        for line in file:
            data = line.strip().split('|')

            # add only if the entry is not an ETF (ETF flag is 'N')
            if data[6] == 'N':
                ticker_symbols.append(data[0])

    ticker_symbols = [symbol.replace('.', '-') for symbol in ticker_symbols]

    return ticker_symbols

file_path = 'nasdaqlisted.txt'
nasdaq_symbols = extract_ticker_symbols(file_path)

file_path = 'otherlisted.txt'
other_symbols = extract_ticker_symbols(file_path)

ticker_symbols = set(nasdaq_symbols + other_symbols)
ticker_symbols = list(ticker_symbols)
ticker_symbols.sort()

df = pd.DataFrame(ticker_symbols, columns=['Ticker'])
df.to_csv('ticker_symbols.csv', index=False)
