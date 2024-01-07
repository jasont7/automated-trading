import pandas as pd
import warnings

warnings.filterwarnings("ignore")

open_df = pd.read_csv('data/data_2020-2024/Open.csv', index_col=0, parse_dates=True)
close_df = pd.read_csv('data/data_2020-2024/Close.csv', index_col=0, parse_dates=True)

# Shift the close_prices DataFrame to align with the next day's open prices
previous_close = close_df.shift(1)

gap_down = (previous_close - open_df) / previous_close

n_stocks = 15
top_gap_down_stocks = gap_down.apply(lambda x: x.nlargest(n_stocks).index, axis=1)
top_gap_up_stocks = gap_down.apply(lambda x: x.nsmallest(n_stocks).index, axis=1)



pct_changes_1 = pd.DataFrame(index=top_gap_down_stocks.index)
for date, stocks in top_gap_down_stocks.iteritems():
    for stock in stocks:
        pct_changes_1.at[date, stock] = 100 * (close_df.at[date, stock] - open_df.at[date, stock]) / open_df.at[date, stock]

pct_changes_2 = pd.DataFrame(index=top_gap_up_stocks.index)
for date, stocks in top_gap_up_stocks.iteritems():
    for stock in stocks:
        pct_changes_2.at[date, stock] = -100 * (close_df.at[date, stock] - open_df.at[date, stock]) / open_df.at[date, stock]

pct_change = pct_changes_1.add(pct_changes_2, fill_value=0)

# Calculate the average percentage change for each day
avg_pct_change_1 = pct_changes_1.mean(axis=1)
avg_pct_change_2 = pct_changes_2.mean(axis=1)
avg_pct_change = pct_change.mean(axis=1)

# savw the average percentage change for each day to a CSV file
avg_pct_change_1.to_csv(f'data/avg_pct_change_1_{n_stocks}.csv')
avg_pct_change_2.to_csv(f'data/avg_pct_change_2_{n_stocks}.csv')
avg_pct_change.to_csv(f'data/avg_pct_change_{n_stocks}.csv')

print(avg_pct_change_1.mean(), avg_pct_change_1.std(), avg_pct_change_1.max(), avg_pct_change_1.min())
print(avg_pct_change_2.mean(), avg_pct_change_2.std(), avg_pct_change_2.max(), avg_pct_change_2.min())
print(avg_pct_change.mean(), avg_pct_change.std(), avg_pct_change.max(), avg_pct_change.min())
