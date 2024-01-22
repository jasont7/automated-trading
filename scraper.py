from playwright.sync_api import sync_playwright
import pandas as pd
import numpy as np
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


def clean_df(df):
    df = df[['No.', 'Ticker', 'Price', 'from Open', 'Gap', 'Volume']]

    from_open = df['from Open'].str.rstrip('%').astype(float)
    df = df[from_open < 1.0] # filter out stocks that gapped up too much

    return df
    

def buy_df(df, num_stocks, budget_per_stock):
    # place an order for each row in df
    df['shares_to_buy'] = np.round(budget_per_stock / df['Price'].astype(float))
    for index, row in df.iterrows():
        if index < num_stocks:
            ibkr.place_order(row['Ticker'], 'BUY', row['shares_to_buy'], 'MKT')


if __name__ == "__main__":
    num_stocks = 10
    budget_per_stock = 100

    buy_time = datetime.time(6, 30, 5)
    buy_time_no_ms = datetime.time(buy_time.hour, buy_time.minute, buy_time.second)

    while True:
        cur_time = datetime.datetime.now().time()
        cur_time_no_ms = datetime.time(cur_time.hour, cur_time.minute, cur_time.second)

        if cur_time_no_ms == buy_time_no_ms:
            df = clean_df(get_finviz_df())
            buy_df(df, num_stocks, budget_per_stock)

            cur_date_str = datetime.date.today().strftime('%Y-%m-%d')
            df.to_csv(f'data/finviz/finviz_{cur_date_str}.csv', index=False)

            time.sleep(60)
        else:
            print(cur_time_no_ms)    
            time.sleep(1)

