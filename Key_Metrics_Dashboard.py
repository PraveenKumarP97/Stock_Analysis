import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

st.set_page_config(layout="wide")
st.title("📊 Key Metrics Dashboard")

engine = create_engine("mysql+pymysql://root:@localhost/stock_market")

# -------------------------------
# 🔝 Top & Bottom 10 Stocks (Calculated in SQL)
# -------------------------------
# We only fetch the 10 rows we actually need
top10_query = "SELECT Ticker, yearly_return FROM sector_data ORDER BY yearly_return DESC LIMIT 10"
bottom10_query = "SELECT Ticker, yearly_return FROM sector_data ORDER BY yearly_return ASC LIMIT 10"

top10 = pd.read_sql(top10_query, engine)
bottom10 = pd.read_sql(bottom10_query, engine)

col1, col2 = st.columns(2)

with col1:
    st.subheader("🟢 Top 10 Green Stocks")
    st.dataframe(top10)

with col2:
    st.subheader("🔴 Top 10 Loss Stocks")
    st.dataframe(bottom10)

# -------------------------------
# 📊 Market Summary (Aggregated in SQL)
# -------------------------------
st.subheader("📌 Market Summary")

# Single query to get all counts and averages at once
summary_query = """
SELECT 
    SUM(CASE WHEN yearly_return > 0 THEN 1 ELSE 0 END) as green_count,
    SUM(CASE WHEN yearly_return < 0 THEN 1 ELSE 0 END) as red_count
FROM sector_data
"""

# Query for stock averages
stock_stats_query = "SELECT AVG(Close) as avg_price, AVG(Volume) as avg_volume FROM stock_data"

summary_df = pd.read_sql(summary_query, engine)
stock_stats_df = pd.read_sql(stock_stats_query, engine)

# Extract values from the dataframes
green_count = summary_df["green_count"].iloc[0]
red_count = summary_df["red_count"].iloc[0]
avg_price = stock_stats_df["avg_price"].iloc[0]
avg_volume = stock_stats_df["avg_volume"].iloc[0]

col3, col4, col5 = st.columns(3)

col3.metric("🟢 Green Stocks", int(green_count))
col4.metric("🔴 Red Stocks", int(red_count))
col5.metric("📊 Avg Price", round(avg_price, 2))

st.metric("📦 Avg Volume", int(avg_volume))