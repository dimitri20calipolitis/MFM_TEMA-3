# -*- coding: utf-8 -*-
"""research-model.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1VMUxogF8edalVKIzGhUjy-JV2S1VfOKh

# Research model
Paper: Preis, T., Moat, H. & Stanley, H.
Quantifying Trading Behavior in Financial Markets Using Google Trends. Sci Rep 3, 1684 (2013). https://doi.org/10.1038/srep01684

Original code: https://github.com/cristianpjensen/stock-market-prediction-via-google-trends

This is the implementation of the model, which is used in the research. However, instead of "debt", I used "stock market". This is because "debt" does not accurately predict the stock market anymore. No change in search volume in the entire period of the corona-virus. "stock market" search volume always changes accordingly.

$$
\Delta n(t, \Delta t) = n(t) - N(t - 1, \Delta t)
$$

$$
N(t - 1, \Delta t) = \frac{n(t-1) + n(t-2) + \cdots + n(t-\Delta t)}{\Delta t}
$$

$$
buy\text{_}signal = \Delta n(t-1, \Delta t) < 0
$$

$$
sell\text{_}signal = \Delta n(t-1, \Delta t) > 0
$$

As can be seen, this implementation has a 23.9% annual return over 16.5 years. This period has seen two major crashes (2008 housing market, 2020 corona-virus). It accurately predicted both of these crashes. A $\Delta t$ of 3 was used.

This is the strategy used by the research in `../references/Quantifying-Trading-Behavior-in-Financial-Markets-Using-Google-Trends.pdf`.
"""

import pandas as pd
import yfinance as yf
import seaborn as sns
import matplotlib.pyplot as plt

trends = pd.read_csv("imprumut.csv", index_col=False)
print(trends)

bet = pd.read_csv("BET.csv", index_col=False)
bet.head()

df = pd.DataFrame()

df["debt"] = trends.Adjusted
df["close"] = bet.reset_index().BET

df["pct_change"] = df.close.pct_change() + 1

print(df)

df["N"] = df.debt.rolling(window=3).mean().shift(1)
df["n"] = df.debt - df.N
print(df)

df["signal"] = ""

for i, data in enumerate(df.n):
    if data > 0:
        df.loc[i, "signal"] = 1
    else:
        df.loc[i, "signal"] = 0

df = df[3:]
df = df.reset_index()
print(df)

i = 0
current_port = 100
current_bh = 100
correct = 0
df["portfolio"] = 0
df["buyhold"] = 0
buy_signals = []
sell_signals = []

while i < len(df):
    if df.signal[i] == 0:
        current_port *= df["pct_change"][i]
        buy_signals.append(i)
        if df["pct_change"][i] > 1:
            correct += 1
    else:
        current_port /= df["pct_change"][i]
        sell_signals.append(i)
        if df["pct_change"][i] < 1:
            correct += 1

    current_bh *= df["pct_change"][i]

    df.loc[i, "portfolio"] = current_port
    df.loc[i, "buyhold"] = current_bh

    i += 1

df["portfolio"].iloc[-1]

print("Annualised Buy-and-Hold Portfolio Return:",
      round(((df["buyhold"].iloc[-1] / 100) ** (1 / (len(df) / 52)) - 1) * 100, 1), "%")

df["portfolio"]

print("Accuracy:", round((correct / len(df)) * 100, 1), "%")
print("Total Return:", round((df["portfolio"][len(df) - 1] / 100) * 100, 1), "%")
print("Annualised Google Portfolio Return::",
      round(((df["portfolio"][len(df) - 1] / 100) ** (1 / (len(df) / 52)) - 1) * 100, 1), "%")

"""# Visualisation
Two visualisations:
1. Google Trends strategy vs. buy-and-hold strategy;
2. Stock price during 
"""

sns.set()

fig, ax = plt.subplots(1, 1, dpi=300)

sns.lineplot(x="index", y="portfolio", data=df, ax=ax, label="Google portfolio")
sns.lineplot(x="index", y="buyhold", data=df, ax=ax, label="Buy and hold portfolio")
ax.legend()
plt.show()

fig, ax = plt.subplots(1, 1, dpi=300)

sns.lineplot(x=df["index"][1:86], y=df["close"], ax=ax)
sns.scatterplot(x=df["index"][1:86], y=df["close"][buy_signals], ax=ax, color="green")
sns.scatterplot(x=df["index"][1:86], y=df["close"][sell_signals], ax=ax, color="red")
plt.show()

