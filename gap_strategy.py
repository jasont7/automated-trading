import pandas as pd
import warnings

warnings.filterwarnings("ignore")


def test_gap_strategy(data_dir, n_stocks, save_data=False, print_stats=False):
    open_df = pd.read_csv(f'{data_dir}/Open.csv', index_col=0, parse_dates=True)
    close_df = pd.read_csv(f'{data_dir}/Close.csv', index_col=0, parse_dates=True)

    # Shift close prices down to align with the next day's open prices
    prev_close = close_df.shift(1)

    # Calculate gap between prev close and next day's open for each stock
    gap_down = (prev_close - open_df) / prev_close

    top_gap_down_stocks = gap_down.apply(lambda x: x.nlargest(n_stocks).index, axis=1)
    top_gap_up_stocks = gap_down.apply(lambda x: x.nsmallest(n_stocks).index, axis=1)

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

    if save_data:
        daily_pct_change_1.to_csv(f'data/daily_pct_change_1_large_{n_stocks}.csv')
        daily_pct_change_2.to_csv(f'data/daily_pct_change_2_large_{n_stocks}.csv')
        daily_pct_change.to_csv(f'data/daily_pct_change_large_{n_stocks}.csv')

    if print_stats:
        print(f'UNIVERSE: {data_dir}')
        print(f'N_STOCKS: {n_stocks}')
        print(f'LONG:  daily avg: {round(daily_pct_change_1.mean(), 3)}%  stdev: {round(daily_pct_change_1.std(), 3)}%  range: [{round(daily_pct_change_1.min(), 3)}%, {round(daily_pct_change_1.max(), 3)}%]')
        print(f'SHORT: daily avg: {round(daily_pct_change_2.mean(), 3)}%  stdev: {round(daily_pct_change_2.std(), 3)}%  range: [{round(daily_pct_change_2.min(), 3)}%, {round(daily_pct_change_2.max(), 3)}%]')
        print(f'COMBO: daily avg: {round(daily_pct_change.mean(), 3)}%  stdev: {round(daily_pct_change.std(), 3)}%  range: [{round(daily_pct_change.min(), 3)}%, {round(daily_pct_change.max(), 3)}%]')

    return {
        'long': (daily_pct_change_1.mean(), daily_pct_change_1.std()),
        'short': (daily_pct_change_2.mean(), daily_pct_change_2.std()),
        'combo': (daily_pct_change.mean(), daily_pct_change.std())
    }


if __name__ == "__main__":
    data_dirs = {
        'small+': 'data/2020-2024_small_plus',
        'mid+': 'data/2020-2024_mid_plus',
        'large+': 'data/2020-2024_large_plus',
    }

    results = []
    for universe, data_dir in data_dirs.items():
        for n_stocks in range(15, 21):
            result = test_gap_strategy(data_dir, n_stocks)
            for key, value in result.items():
                daily_avg, daily_std = value
                results.append((daily_avg, daily_std, universe, n_stocks, key))
    
    results_df = pd.DataFrame(results, columns=['daily_avg', 'daily_std', 'universe', 'n_stocks', 'strategy'])
    results_df.to_csv('data/results.csv', index=False)
