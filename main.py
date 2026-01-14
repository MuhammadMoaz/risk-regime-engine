import yfinance as yf
import pandas as pd

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
    daily_returns = btc_hist['Close'].pct_change()
    btc_hist['Daily Returns'] = daily_returns

    # Calculating 7 day rolling volatility
    

    print(btc_hist.info)


main()