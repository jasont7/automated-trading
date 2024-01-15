from playwright.sync_api import sync_playwright
import pandas as pd
import time
import os
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv('FINVIZ_USER')
PASS = os.getenv('FINVIZ_PASS')

def run(playwright):
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
    df.to_csv('data/finviz.csv', index=False)

    browser.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
