import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px

st.set_page_config(layout="wide")
st.title("📈 Advanced Stock Analysis")

engine = create_engine("mysql+pymysql://root:@localhost/stock_market")

# -------------------------------
# 1️⃣ Volatility Analysis (SQL)
# -------------------------------
st.subheader("1️⃣ Volatility Analysis")

# SQL calculates daily returns and then the standard deviation per Ticker
volatility_query = """
WITH DailyReturns AS (
    SELECT 
        Ticker,
        (Close - LAG(Close) OVER (PARTITION BY Ticker ORDER BY Date)) / LAG(Close) OVER (PARTITION BY Ticker ORDER BY Date) as daily_ret
    FROM stock_data
)
SELECT Ticker, STDDEV(daily_ret) as volatility
FROM DailyReturns
WHERE daily_ret IS NOT NULL
GROUP BY Ticker
ORDER BY volatility DESC
LIMIT 10
"""
volatility_df = pd.read_sql(volatility_query, engine)
fig1 = px.bar(volatility_df, x="Ticker", y="volatility", title="Top 10 Most Volatile Stocks")
st.plotly_chart(fig1, use_container_width=True)

st.divider()

# -------------------------------
# 2️⃣ Cumulative Return Over Time (SQL)
# -------------------------------
st.subheader("2️⃣ Cumulative Return Over Time")

# SQL identifies top 5 based on total growth, then fetches their full history
cum_ret_query = """
WITH TickerGrowth AS (
    SELECT Ticker,
           (LAST_VALUE(Close) OVER(PARTITION BY Ticker ORDER BY Date ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) / 
            FIRST_VALUE(Close) OVER(PARTITION BY Ticker ORDER BY Date ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) - 1) as total_growth
    FROM stock_data
),
Top5Tickers AS (
    SELECT DISTINCT Ticker FROM TickerGrowth ORDER BY total_growth DESC LIMIT 5
)
SELECT Date, Ticker, 
       (Close / FIRST_VALUE(Close) OVER (PARTITION BY Ticker ORDER BY Date) - 1) as cumulative_return
FROM stock_data
WHERE Ticker IN (SELECT Ticker FROM Top5Tickers)
"""
df_top5 = pd.read_sql(cum_ret_query, engine)
df_top5["Date"] = pd.to_datetime(df_top5["Date"])
fig2 = px.line(df_top5, x="Date", y="cumulative_return", color="Ticker")
st.plotly_chart(fig2, use_container_width=True)

st.divider()

# -------------------------------
# 3️⃣ Sector-wise Performance (SQL)
# -------------------------------
st.subheader("3️⃣ Sector-wise Performance")

sector_query = """
SELECT sector, AVG(yearly_return) as avg_yearly_return
FROM sector_data
GROUP BY sector
ORDER BY avg_yearly_return DESC
"""
sector_avg = pd.read_sql(sector_query, engine)
fig3 = px.bar(sector_avg, x="sector", y="avg_yearly_return")
st.plotly_chart(fig3, use_container_width=True)

st.divider()

# -------------------------------
# 4️⃣ Stock Price Correlation (Seaborn Optimized)
# -------------------------------
import seaborn as sns
import matplotlib.pyplot as plt

st.subheader("4️⃣ Stock Price Correlation")

# Fetch data and clean in Pandas (necessary for matrix math)
corr_query = "SELECT Date, Ticker, Close FROM stock_data"
df_corr = pd.read_sql(corr_query, engine)

# Preparing the pivot table and correlation matrix (as before)
# We pivot to get Dates as rows, Tickers as columns
# Then calculate percentage change, and finally correlation.
pivot_df = df_corr.pivot(index="Date", columns="Ticker", values="Close")
corr_matrix = pivot_df.pct_change().corr()

# Count tickers for dynamic sizing
num_tickers = len(corr_matrix.columns)

# -------------------------------
# 🔧 HEATMAP CUSTOMIZATION
# -------------------------------

import seaborn as sns
import matplotlib.pyplot as plt

# Ensure Tickers are clean to avoid duplicate/messy axes
df_corr = pd.read_sql("SELECT Date, Ticker, Close FROM stock_data", engine)
df_corr["Ticker"] = df_corr["Ticker"].str.strip().str.upper()

pivot_df = df_corr.pivot(index="Date", columns="Ticker", values="Close")
corr_matrix = pivot_df.pct_change().corr()

# Define the figure size
num_tickers = len(corr_matrix.columns)
fig, ax = plt.subplots(figsize=(12, 12)) # Equal numbers for a square canvas

# Force the exact color behavior
sns.heatmap(
    corr_matrix,
    cmap="coolwarm",    # Diverging palette
    vmin=0,             # Minimum value for the scale (usually 0 for price corr)
    vmax=1,             # Maximum value for the scale (Perfect correlation)
    center=0.5,         # The point where colors transition (try 0.5 or 0.6)
    square=True,        # Keep it a perfect square
    annot=False,        # Numbers make it messy if you have many stocks
    linewidths=.5,      # Thin lines between squares
    cbar_kws={"shrink": .8},
    ax=ax
)

# Force the ticks to be readable
plt.xticks(rotation=90)
plt.yticks(rotation=0)

st.pyplot(fig)


st.subheader("🔝 Top 10 Stocks Correlation")

# 1. Calculate cumulative returns to find the "Top 10"
# (1 + returns).prod() gives the total return multiplier
returns_df = pivot_df.pct_change()
cumulative_returns = (1 + returns_df).prod().sort_values(ascending=False)

# 2. Extract the tickers for the top 10 performers
top_10_tickers = cumulative_returns.head(10).index
top_10_corr_matrix = returns_df[top_10_tickers].corr()

# 3. Create the Visualization
fig_top, ax_top = plt.subplots(figsize=(10, 8))

sns.heatmap(
    top_10_corr_matrix,
    cmap="coolwarm",      # Different palette (Red-Yellow-Green) to distinguish from the full set
    vmin=0, 
    vmax=1, 
    center=0.5,
    square=True,
    annot=True,         # We enable annotations since 10x10 is readable
    fmt=".2f",          # Limit to 2 decimal places
    linewidths=1,
    cbar_kws={"shrink": .8},
    ax=ax_top
)

ax_top.set_title("Correlation of Top 10 Performers (By Returns)")
st.pyplot(fig_top)

st.divider()

# -------------------------------
# 5️⃣ Monthly Top Gainers & Losers (SQL)
# -------------------------------
st.subheader("5️⃣ Monthly Top Gainers & Losers")

# Get available months for the dropdown
month_list = pd.read_sql("SELECT DISTINCT DATE_FORMAT(Date, '%%Y-%%m') as month FROM stock_data ORDER BY month DESC", engine)
selected_month = st.selectbox("Select Month", month_list['month'])

# SQL calculates the return based on the first and last price of the selected month
monthly_query = f"""
WITH MonthBounds AS (
    SELECT 
        Ticker,
        FIRST_VALUE(Close) OVER (PARTITION BY Ticker ORDER BY Date) as first_p,
        LAST_VALUE(Close) OVER (PARTITION BY Ticker ORDER BY Date ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) as last_p
    FROM stock_data
    WHERE DATE_FORMAT(Date, '%%Y-%%m') = '{selected_month}'
)
SELECT DISTINCT Ticker, ((last_p - first_p) / first_p) * 100 as monthly_return
FROM MonthBounds
ORDER BY monthly_return DESC
"""
month_results = pd.read_sql(monthly_query, engine)

col1, col2 = st.columns(2)
with col1:
    top5 = month_results.head(5)
    st.write("🟢 Top 5 Gainers")
    st.plotly_chart(px.bar(top5, x="Ticker", y="monthly_return", color_continuous_scale="Greens"), use_container_width=True)
with col2:
    bottom5 = month_results.tail(5)
    st.write("🔴 Top 5 Losers")
    st.plotly_chart(px.bar(bottom5, x="Ticker", y="monthly_return", color_continuous_scale="Reds"), use_container_width=True)