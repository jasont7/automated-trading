from playwright.sync_api import sync_playwright
import pandas as pd
import numpy as np
import yfinance as yf
import time
import datetime
import os
from dotenv import load_dotenv
import ibkr

load_dotenv()

USERNAME = os.getenv('FINVIZ_USER')
PASS = os.getenv('FINVIZ_PASS')


def get_finviz_df():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()

        # Login to Finviz
        page.goto("https://finviz.com/login.ashx")
        page.fill("input[name='email']", USERNAME)
        page.fill("input[name='password']", PASS)
        page.click("input[type='submit']")

        # Go to screener and get table html (small+, 100k+ avg volume)
        page.goto("https://elite.finviz.com/screener.ashx?v=171&f=cap_smallover,sh_avgvol_o100&o=gap")
        table_html = page.query_selector('#screener-table > td > table').inner_html()

        # Convert table html to dataframe
        df = pd.read_html(f"<table>{table_html}</table>")[0]
        df = df.iloc[2:].reset_index(drop=True)
        print(df.head(20))

        return df


def get_yfin_df(n_stocks):
    tickers = pd.read_csv('data/tickers/tickers_small_plus.csv', squeeze=True).dropna().to_list()
    df = yf.download(tickers, period='2d', auto_adjust=True)
    for attribute in ['Open', 'Close', 'Volume']:
        df[attribute].to_csv(f'data/tmp/{attribute}.csv')
    
    open_df = pd.read_csv(f'data/tmp/Open.csv', index_col=0, parse_dates=True)
    close_df = pd.read_csv(f'data/tmp/Close.csv', index_col=0, parse_dates=True)

    # Shift close prices down to align with the next day's open prices
    prev_close = close_df.shift(1)

    # Calculate gap between prev close and next day's open for each stock
    gap_down = (prev_close - open_df) / prev_close

    top_gap_down_stocks = gap_down.apply(lambda x: x.nlargest(n_stocks).index, axis=1).iloc[-1].values.tolist()
    # top_gap_up_stocks = gap_down.apply(lambda x: x.nsmallest(n_stocks).index, axis=1).iloc[-1].values.tolist()

    prev_close_prices = prev_close[top_gap_down_stocks].iloc[-1]
    open_prices = open_df[top_gap_down_stocks].iloc[-1]
    last_prices = close_df[top_gap_down_stocks].iloc[-1]

    result_df = pd.DataFrame({
        'Ticker': last_prices.index,
        'PrevClose': prev_close_prices.values,
        'Open': open_prices.values,
        'Price': last_prices.values,
    })

    return result_df


def clean_df(df):
    df = df[['No.', 'Ticker', 'Price', 'from Open', 'Gap', 'Volume']]

    from_open = df['from Open'].str.rstrip('%').astype(float)
    df = df[from_open < 1.0] # filter out stocks that gapped up too much
    df = df.reset_index(drop=True)

    return df
    

def buy_df(df, num_stocks, budget_per_stock):
    # place an order for each row in df
    df['shares_to_buy'] = np.round(budget_per_stock / df['Price'].astype(float))
    for index, row in df.iterrows():
        if index < num_stocks:
            ibkr.place_order(row['Ticker'], 'BUY', row['shares_to_buy'], 'MKT')


if __name__ == "__main__":
    num_stocks = 12
    budget_per_stock = 100

    buy_time = datetime.time(6, 30, 5)  # wait 5 seconds for stock list to settle
    buy_time_no_ms = datetime.time(buy_time.hour, buy_time.minute, buy_time.second)

    while True:
        cur_time = datetime.datetime.now().time()
        cur_time_no_ms = datetime.time(cur_time.hour, cur_time.minute, cur_time.second)

        if cur_time_no_ms == buy_time_no_ms:
            df = clean_df(get_finviz_df())
            # df = get_yfin_df(num_stocks)
            buy_df(df, num_stocks, budget_per_stock)

            cur_date_str = datetime.date.today().strftime('%Y-%m-%d')
            df.to_csv(f'data/daily/{cur_date_str}.csv', index=False)

            time.sleep(60)
        else:
            print(cur_time_no_ms)    
            time.sleep(1)

