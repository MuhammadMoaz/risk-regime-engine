import yfinance as yf
import pandas as pd

def fetch_data(ticker):
    # data = yf.download(ticker, period=max, multi_level_index=False)
    btc = yf.Ticker("BTC-USD")
    btc_hist = btc.history(period="max")
    fname = ticker + "_data.csv"
    btc_hist.to_csv(fname)

def main():
    fetch_data("BTC-USD")

main()