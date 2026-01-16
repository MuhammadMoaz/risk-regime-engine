import yfinance as yf
import pandas as pd
import numpy as np

def fetch_data():
    print()

def add_returns_and_vol(data):
    print()
    
def main():
    # btc_hist = fetch_data("BTC-USD")
    # get_daily_returns(btc_hist)

    btc = yf.Ticker("BTC-USD")
    btc_hist = btc.history(period="max")
    print(btc_hist.info)

    # Dropping empty columns (Dividends and Stock Splits)
    btc_hist.drop(['Dividends', 'Stock Splits'], axis=1, inplace=True)
    
    # Calculating daily returns and inserting values as new column
    daily_returns = (btc_hist['Close'] / btc_hist['Close'].shift(1)) - 1
    btc_hist['Daily Returns'] = daily_returns

    # Calculating 7 day rolling volatility
    # 1. Get logarithmic daily returns
    log_daily_returns = np.log(btc_hist['Close'] / btc_hist['Close'].shift(1))
    btc_hist['Daily Log Returns'] = log_daily_returns

    # 2. Get average of returns for 7 day window
    btc_hist['7 Day Avg Log Return'] = btc_hist['Daily Log Returns'].rolling(window=7).mean()

    # 3. Roll the window (2->8, 3->9, etc)
    btc_hist['7 Day Rolling Volatility'] = btc_hist['Daily Log Returns'].rolling(window=7).std()

    # 4. (Optional) annualize volatility
    btc_hist['7 Day Rolling Volatility Ann'] = (btc_hist['7 Day Rolling Volatility'] * np.sqrt(365))

    print(btc_hist.tail(10))


main()