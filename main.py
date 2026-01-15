import yfinance as yf
import pandas as pd
import numpy as np

def fetch_data(ticker):
    print()

def get_daily_returns(data):
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
    btc_hist['Log Daily Returns'] = log_daily_returns
    # 2. Get average of returns for 7 day window
    # 3. Calc sample stdev
    # 4. (Optional) annualize volatility
    # 5. Roll the window (2->8, 3->9, etc)

    print(btc_hist.info)


main()