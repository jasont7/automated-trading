from playwright.sync_api import sync_playwright
import pandas as pd
import numpy as np
import time
from datetime import datetime, time as dtime
import os
from dotenv import load_dotenv
import ibkr

load_dotenv()

USERNAME = os.getenv('FINVIZ_USER')
PASS = os.getenv('FINVIZ_PASS')


def get_finviz_df(playwright):
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()

    # Login to Finviz
    page.goto("https://finviz.com/login.ashx")
    page.fill("input[name='email']", USERNAME)
    page.fill("input[name='password']", PASS)
    page.click("input[type='submit']")

    # Go to screener and get table html
    page.goto("https://elite.finviz.com/screener.ashx?v=171&f=cap_smallover&o=gap")
    table_html = page.query_selector('#screener-table > td > table').inner_html()

    # Convert table html to dataframe
    df = pd.read_html(f"<table>{table_html}</table>")[0]
    df = df.iloc[2:].reset_index(drop=True)
    print(df.head(20))

    browser.close()

    return df


def df_to_buy(df, num_stocks, budget_per_stock):
    # place an order for each row in df
    df['shares_to_buy'] = np.round(budget_per_stock / df['Price'].astype(float))

    for index, row in df.iterrows():
        if index < num_stocks:
            ibkr.place_order(row['Ticker'], 'BUY', row['shares_to_buy'], 'MKT')


if __name__ == "__main__":
    df = pd.DataFrame()

    num_stocks = 10
    budget_per_stock = 100
    
    buy_time = dtime(6, 30, 2)
    buy_time_no_ms = dtime(buy_time.hour, buy_time.minute, buy_time.second)

    while True:
        cur_time = datetime.now().time()
        cur_time_no_ms = dtime(cur_time.hour, cur_time.minute, cur_time.second)

        if cur_time_no_ms == buy_time_no_ms:
            with sync_playwright() as playwright:
                df = get_finviz_df(playwright)

            df.to_csv('data/finviz.csv', index=False)
            
            df_to_buy(df, num_stocks, budget_per_stock)

            time.sleep(60)
        else:
            print(cur_time_no_ms)    
            time.sleep(1)

