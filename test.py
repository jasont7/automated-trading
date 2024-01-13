import pandas as pd
import warnings

warnings.filterwarnings("ignore")

INPUT_DATA_DIR = 'data/data_2020-2024_large'
N_STOCKS = 5

open_df = pd.read_csv(f'{INPUT_DATA_DIR}/Open.csv', index_col=0, parse_dates=True)
close_df = pd.read_csv(f'{INPUT_DATA_DIR}/Close.csv', index_col=0, parse_dates=True)

# Shift close prices down to align with the next day's open prices
prev_close = close_df.shift(1)

# Calculate gap between prev close and next day's open for each stock
gap_down = (prev_close - open_df) / prev_close

top_gap_down_stocks = gap_down.apply(lambda x: x.nlargest(N_STOCKS).index, axis=1)
top_gap_up_stocks = gap_down.apply(lambda x: x.nsmallest(N_STOCKS).index, axis=1)

# Calculate the percentage change from open to close for each top-n stock
pct_changes_1 = pd.DataFrame(index=top_gap_down_stocks.index)  # long gap down
for date, stocks in top_gap_down_stocks.iteritems():
    for stock in stocks:
        pct_changes_1.at[date, stock] = 100 * (close_df.at[date, stock] - open_df.at[date, stock]) / open_df.at[date, stock]

pct_changes_2 = pd.DataFrame(index=top_gap_up_stocks.index)  # short gap up
for date, stocks in top_gap_up_stocks.iteritems():
    for stock in stocks:
        pct_changes_2.at[date, stock] = -100 * (close_df.at[date, stock] - open_df.at[date, stock]) / open_df.at[date, stock]

# Combine long (1) and short (2)
pct_change = pct_changes_1.add(pct_changes_2, fill_value=0)

# Calculate the avg % change across all stocks for each day
daily_pct_change_1 = pct_changes_1.mean(axis=1)
daily_pct_change_2 = pct_changes_2.mean(axis=1)
daily_pct_change = pct_change.mean(axis=1)

daily_pct_change_1.to_csv(f'data/daily_pct_change_1_large_{N_STOCKS}.csv')
daily_pct_change_2.to_csv(f'data/daily_pct_change_2_large_{N_STOCKS}.csv')
daily_pct_change.to_csv(f'data/daily_pct_change_large_{N_STOCKS}.csv')

# Statistics
print(daily_pct_change_1.mean(), daily_pct_change_1.std(), daily_pct_change_1.max(), daily_pct_change_1.min())
print(daily_pct_change_2.mean(), daily_pct_change_2.std(), daily_pct_change_2.max(), daily_pct_change_2.min())
print(daily_pct_change.mean(), daily_pct_change.std(), daily_pct_change.max(), daily_pct_change.min())
