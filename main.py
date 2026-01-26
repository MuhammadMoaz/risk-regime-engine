import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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

    # 4. annualize volatility
    btc_hist['7 Day Rolling Volatility Ann'] = (btc_hist['7 Day Rolling Volatility'] * np.sqrt(365))

    print(btc_hist.tail(10))

    # Plot
    # Pick threshold (80th percentile)
    vol = btc_hist['7 Day Rolling Volatility'].dropna()
    threshold = vol.quantile(0.8)
    btc_hist['High Volatility'] = btc_hist['7 Day Rolling Volatility'] >= threshold

    print("High vol %:", btc_hist['High Volatility'].mean())
    print("Threshold:", threshold)

    # Plot the close data
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(btc_hist.index, btc_hist['Close'], linewidth=1)
    ax.set_xlabel("BTC Close")
    ax.set_ylabel("Date")
    ax.set_title("Close Series")

    # Shade the high vol areas
    mask = btc_hist['High Volatility'].fillna(False)
    change = mask.ne(mask.shift()).cumsum()
    high_groups = btc_hist[mask].groupby(change)

    for _, grp in high_groups:
        start = grp.index[0]
        end = grp.index[-1]
        ax.axvspan(start, end, facecolor='purple', alpha=0.2)

    plt.savefig(f"Plots/BTC_Figure.png")
    plt.clf()

    # Market Regime Clasifying
    btc_hist['MA_50'] = btc_hist['Close'].rolling(window=50).mean()

    # Regime 1: Up Trend
    btc_hist['Trend Up'] = btc_hist['Close'] > btc_hist['MA_50']

    # Regime 2: Down Trend
    btc_hist['Trend Down'] = btc_hist['Close'] < btc_hist['MA_50']

    # Regime Assignment
    btc_hist['Regime'] = None

    # Rule 1: High Volatility
    btc_hist.loc[btc_hist['High Volatility'], 'Regime'] = 'HIGH_VOL'

    # Rule 2: Calm + uptrend
    btc_hist.loc[
        (~btc_hist['High Volatility']) & (btc_hist['Trend Up']),
        'Regime'
    ] = "CALM UP"

    # Rule 3: Calm + downtrend
    btc_hist.loc[
        btc_hist['Regime'].isna(),
        'Regime'
    ] = 'CALM_DOWN'

    print(btc_hist['Regime'].value_counts(normalize=True))

    # Visualise BTC Close shaded by regime
    regime_colours = {
        'HIGH_VOL': 'purple',
        'CALM_UP': 'green',
        'CALM_DOWN': 'red'
    }

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(btc_hist.index, btc_hist['Close'], linewidth=1)
    ax.set_title("BTC Close with Regime Shading")
    ax.set_xlabel("BTC Close")
    ax.set_ylabel("Date")

    regime_series = btc_hist['Regime'].fillna('NONE')

    change = regime_series.ne(regime_series.shift()).cumsum()
    groups = btc_hist.groupby(change)

    for _, grp in groups:
        regime = grp['Regime'].iloc[0]

        if regime not in regime_colours:
            continue

        start = grp.index[0]
        end = grp.index[-1]

        ax.axvspan(start, end, facecolor=regime_colours[regime], alpha=0.15)

    plt.savefig("Plots/BTC_Regime_Shaded.png")
    plt.clf()

    # Calculating Forward Returns
    btc_hist['Fwd_7D'] = btc_hist['Close'].shift(-7) / btc_hist['Close'] - 1
    btc_hist['Fwd_14D'] = btc_hist['Close'].shift(-14) / btc_hist['Close'] - 1
    btc_hist['Fwd_30D'] = btc_hist['Close'].shift(-30) / btc_hist['Close'] - 1

    analysis_7d = btc_hist.dropna(subset=['Regime', 'Fwd_7D'])
    analysis_14d = btc_hist.dropna(subset=['Regime', 'Fwd_14D'])
    analysis_30d = btc_hist.dropna(subset=['Regime', 'Fwd_30D'])
    
    summary_7d = analysis_7d.groupby('Regime')['Fwd_7D'].agg(
        mean='mean',
        median='median',
        std='std',
        win_rate=lambda x: (x > 0).mean(),
        count='count'
    )

    summary_14d = analysis_14d.groupby('Regime')['Fwd_14D'].agg(
        mean='mean',
        median='median',
        std='std',
        win_rate=lambda x: (x > 0).mean(),
        count='count'
    )

    summary_30d = analysis_30d.groupby('Regime')['Fwd_30D'].agg(
        mean='mean',
        median='median',
        std='std',
        win_rate=lambda x: (x > 0).mean(),
        count='count'
    )

    print(summary_7d)
    print(summary_14d)
    print(summary_30d)

    analysis_7d.boxplot(column='Fwd_7D', by='Regime', grid=False)
    plt.title('7D Forward Returns by Regime')
    plt.suptitle('')
    plt.ylabel('Forward Return')
    plt.show()
    
    ## Regime to Tradeable Stratgey
    

main()