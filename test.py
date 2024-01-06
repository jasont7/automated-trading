import pandas as pd

open_df = pd.read_csv('data/data_2020-2024/Open.csv', index_col=0, parse_dates=True)
close_df = pd.read_csv('data/data_2020-2024/Close.csv', index_col=0, parse_dates=True)

# Shift the close_prices DataFrame to align with the next day's open prices
previous_close = close_df.shift(1)

# Calculate the gap down (previous close - today's open)
gap_down = previous_close - open_df

# On the first trading day, there won't be a previous close, so fill NaN values with zeros
gap_down.fillna(0, inplace=True)

# Find the top stocks with the maximum gap down for each day
# Assuming you want the top 5 stocks for each day
top_gap_down_stocks = gap_down.apply(lambda x: x.nlargest(5).index, axis=1)

# top_gap_down_stocks now holds the tickers of the top 5 gap down stocks for each day
print(top_gap_down_stocks)


price_diff_to_close = pd.DataFrame(index=top_gap_down_stocks.index)

# Iterate through each day
for date, stocks in top_gap_down_stocks.iteritems():
    # Iterate through each stock for the given day
    for stock in stocks:
        # Calculate the difference between close and open prices
        price_diff = (close_df.at[date, stock] - open_df.at[date, stock]) / open_df.at[date, stock]
        price_diff_to_close.at[date, stock] = price_diff

# 'price_diff_to_close' now contains the price differences for each top gap down stock
print(price_diff_to_close)


percentage_changes = pd.DataFrame(index=price_diff_to_close.index)

# Calculate percentage changes
for date in price_diff_to_close.index:
    for stock in price_diff_to_close.columns:
        if pd.notna(price_diff_to_close.at[date, stock]):
            open_price = open_df.at[date, stock]
            price_diff = price_diff_to_close.at[date, stock]
            percentage_change = (price_diff / open_price) * 100
            percentage_changes.at[date, stock] = percentage_change

# Calculate the average percentage change for each day
average_percentage_change = percentage_changes.mean(axis=1)

# 'average_percentage_change' now contains the average percentage change for each day
print(average_percentage_change)
