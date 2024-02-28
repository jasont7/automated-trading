from playwright.sync_api import sync_playwright
import pandas as pd
import numpy as np
import yfinance as yf
import time
import datetime
import os
from dotenv import load_dotenv
import ibkr
from io import StringIO

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
        # page.goto("https://elite.finviz.com/screener.ashx?v=171&f=cap_midover&o=gap")
        table_html = page.query_selector('#screener-table > td > table').inner_html()

        # Convert table html to dataframe
        df = pd.read_html(StringIO(f"<table>{table_html}</table>"))[0]
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
    df = df[['No.', 'Ticker', 'Price', 'from Open', 'Gap', 'Volume']].copy()

    # filter out stocks that are not real gap-downs
    to_drop = []
    for i, row in df.iterrows():
        try:
            ticker = row['Ticker']
            stock_history = yf.Ticker(ticker).history(period="2d")
            if not stock_history.empty:
                prev_close = stock_history.iloc[0]['Close']
                curr_price = float(row['Price'])
                real_gap_pct = (curr_price - prev_close) / prev_close * 100
                if real_gap_pct > -3.0:
                    print(f"Removing {ticker} because it's not a real gap down")
                    to_drop.append(i)
        except Exception as e:
            print(f"Error with {ticker}: {e}")
            to_drop.append(i)

    df.drop(to_drop, inplace=True)
    df = df.reset_index(drop=True)

    return df
    

def buy_df(df, num_stocks, budget_per_stock):
    # Place an order for each row in df
    # Returns a set of the tickers that were bought
    buys = set()

    df['shares_to_buy'] = np.round(budget_per_stock / df['Price'].astype(float))
    for index, row in df.iterrows():
        if index < num_stocks:
            ibkr.place_order(row['Ticker'], 'BUY', row['shares_to_buy'], 'MKT')
            buys.add(row['Ticker'])
    
    return buys


def sell_positions(buys):
    # Sell all positions that are in the buys set
    positions = ibkr.get_positions()
    to_sell = buys.intersection(positions.keys())
    for ticker in to_sell:
        ibkr.place_order(ticker, 'SELL', positions[ticker]['position'], 'MOC')

    cur_date_str = datetime.date.today().strftime('%Y-%m-%d')
    pd.DataFrame(positions).T.to_csv(f'data/positions/{cur_date_str}.csv')


if __name__ == "__main__":
    num_stocks = 12
    budget_per_stock = 340

    buy_time = datetime.time(6, 30, 5)  # wait 5 seconds for stock list to settle
    buy_time_no_ms = datetime.time(buy_time.hour, buy_time.minute, buy_time.second)

    testing = False

    while True:
        cur_time = datetime.datetime.now().time()
        cur_time_no_ms = datetime.time(cur_time.hour, cur_time.minute, cur_time.second)

        if cur_time_no_ms == buy_time_no_ms or testing:
            df = clean_df(get_finviz_df())
            # df = get_yfin_df(num_stocks)
            buys = buy_df(df, num_stocks, budget_per_stock)

            cur_date_str = datetime.date.today().strftime('%Y-%m-%d')
            df.to_csv(f'data/daily/{cur_date_str}.csv', index=False)

            time.sleep(1800)

            sell_positions(buys)
        else:
            print(cur_time_no_ms)    
            time.sleep(1)

