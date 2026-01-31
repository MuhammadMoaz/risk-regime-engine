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
        mean="mean",
        median="median",
        std="std",
        win_rate=lambda x: (x > 0).mean(),
        count="count"
    )

    summary_14d = analysis_14d.groupby('Regime')['Fwd_14D'].agg(
        mean="mean",
        median="median",
        std="std",
        win_rate=lambda x: (x > 0).mean(),
        count="count"
    )

    summary_30d = analysis_30d.groupby('Regime')['Fwd_30D'].agg(
        mean="mean",
        median="median",
        std="std",
        win_rate=lambda x: (x > 0).mean(),
        count="count"
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
    # Choose horizon to trade on
    HORIZON = '7D'

    if HORIZON == "7D":
        summary = summary_7d.copy()
        fwd_col = "Fwd_7D"
    elif HORIZON == "14D":
        summary = summary_14d.copy()
        fwd_col = "Fwd_14D"
    elif HORIZON == "30D":
        summary = summary_30d.copy()
        fwd_col = "Fwd_30D"
    else:
        raise ValueError("Invalid Horizon")
    
    # risk adjusted scoring
    # Sharpe like score
    summary["risk_adjusted_score"] = summary["mean"] / summary["std"]

    # confidence weighting
    summary["confidence_weight"] = np.log(summary["count"])

    # final score
    summary["final_score"] = summary["risk_adjusted_score"] * summary["confidence_weight"]

    print(summary[["mean", "std", "count", "final_score"]])

    # converting scores to signals

    high_thresh = summary["final_score"].quantile(0.66)
    low_thresh = summary["final_score"].quantile(0.33)

    def score_to_signal(score):
        if score >= high_thresh:
            return "RISK_ON"
        elif score <= low_thresh:
            return "RISK_OFF"
        else:
            return "NEUTRAL"
        
    summary["Signal"] = summary["final_score"].apply(score_to_signal)

    print(summary[["final_score", "Signal"]])

    # mapping signals back to time series

    regime_to_signal = summary["Signal"].to_dict()
    btc_hist["Signal"] = btc_hist["Regime"].map(regime_to_signal)

    print(btc_hist["Signal"].value_counts(normalize=True))

    # forward performance by signal (checks)

    signal_perf = (
        btc_hist
        .dropna(subset=[fwd_col, "Signal"])
        .groupby("Signal")[fwd_col]
        .agg(
            mean="mean",
            median="median",
            std="std",
            win_rate=lambda x: (x>0).mean(),
            count="count"
        )
    )

    print(signal_perf)

    # visualising signal shading

    signal_colours = {
        "RISK_ON": "green",
        "NEUTRAL": "grey",
        "RISK_OFF": "red"
    }

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(btc_hist.index, btc_hist["Close"], linewidth=1)
    ax.set_title(f"BTC Close with Signal Shading ({HORIZON})")
    ax.set_xlabel("Date")
    ax.set_ylabel("BTC Close")

    signal_series = btc_hist["Signal"].fillna("NONE")
    change = signal_series.ne(signal_series.shift()).cumsum()
    groups = btc_hist.groupby(change)

    for _, grp in groups:
        sig = grp["Signal"].iloc[0]

        if sig not in signal_colours:
            continue

        ax.axvspan(
            grp.index[0],
            grp.index[-1],
            facecolor=signal_colours[sig],
            alpha=0.12
        )

    plt.savefig(f"Plots/BTC_Signal_Shaded_{HORIZON}.png")
    plt.clf()

    # actionable output

    latest = btc_hist.dropna(subset=["Signal"]).iloc[-1]

    print("Date:", latest.name.date())
    print("Regime:", latest["Regime"])
    print("Signal:", latest["Signal"])

    # Phase 4 Backtesting
    # Convert signals to position sizes
    signal_to_position = {
        "RISK_ON": 1.0,
        "NEUTRAL": 0.5,
        "RISK_OFF": 0.0
    }

    btc_hist["Position"] = btc_hist["Signal"].map(signal_to_position)
    print(btc_hist[["Signal", "Position"]].dropna().head())

    # Compute daily returns
    btc_hist["Strategy Return"] = (
        btc_hist["Daily Returns"] * btc_hist["Position"]
    )

    print(
        btc_hist[["Daily Returns", "Position", "Strategy Return"]]
        .dropna()
        .head()
    )

    # calculate compound returns (equity curves)
    btc_hist["Strategy Equity"] = (
        1 + btc_hist["Strategy Return"]
    ).cumprod()

    btc_hist["BuyHold Equity"] = (
        1 + btc_hist["Daily Returns"]
    ).cumprod()

    print(
        btc_hist[["Strategy Equity", "BuyHold Equity"]]
        .dropna()
        .tail()
    )

    # visualising equirty curves
    fig, ax = plt.subplots(figsize=(14, 6))

    ax.plot(
        btc_hist.index,
        btc_hist["BuyHold Equity"],
        label="Buy and Hold",
        alpha=0.7
    )

    ax.plot(
        btc_hist.index,
        btc_hist["Strategy Equity"],
        label="Regime Strategy",
        alpha=0.9
    )

    ax.set_title("Equity Curve: Strategy vs Buy and Hold")
    ax.set_xlabel("Growth of $1")
    ax.set_ylabel("Date")
    ax.legend()

    plt.savefig("Plots/BTC_Phase4_Equity.png")
    plt.clf()

main()