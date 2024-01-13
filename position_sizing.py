import pandas as pd
import numpy as np
import yfinance as yf
import ta


def calculate_position(total_capital, risk_percentage, position_size_percent_limit, stock_price, atr, atr_multiple):
    # calculate position size and stop loss price based on volatility
    dollar_risk_per_share = atr_multiple * atr
    stop_loss_price = stock_price - dollar_risk_per_share  # for a long position
    risk_amount = total_capital * risk_percentage
    position_size = risk_amount / dollar_risk_per_share

    # limit position size
    position_amount = position_size * stock_price
    position_amount_limit = total_capital * position_size_percent_limit
    if position_amount > position_amount_limit:
        position_size = position_amount_limit / stock_price

    return position_size, stop_loss_price


def run_system(total_capital, risk_percentage, max_positions, position_size_percent_limit, atr_multiple):
    ticker = "IBM"
    df = yf.download(ticker, start="2023-09-01", end="2024-01-01")

    df['ATR'] = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'], window=14)

    position_size, stop_loss = calculate_position(
        total_capital,
        risk_percentage,
        position_size_percent_limit,
        df['Adj Close'].iloc[-1],
        df['ATR'].iloc[-1],
        atr_multiple
    )

    print(df.tail())
    print()
    print(f"Buy {position_size} shares of {ticker} with stop loss ${stop_loss}")


if __name__ == "__main__":
    run_system(
        total_capital = 100000,
        risk_percentage = 0.02,
        max_positions = 10,
        position_size_percent_limit = 0.10,
        atr_multiple = 2,
    )
