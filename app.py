import streamlit as st

st.set_page_config(page_title="Stock Dashboard", layout="wide")

st.title("📈 Stock Market Analysis Dashboard")

st.markdown("""
### Welcome 👋

This dashboard provides insights into:
- Top performing stocks
- Sector trends
- Volatility & risk
- Correlation analysis
            
*This project is a comprehensive **Stock Market Analysis Dashboard** built using Python, SQL, and Streamlit to analyze and visualize stock performance over a year. The data was processed from raw files, cleaned, and stored in a MySQL database, enabling efficient querying and analysis. Key insights include top gainers and losers, volatility analysis, cumulative returns, sector-wise performance, correlation between stocks, and month-wise trends. Interactive visualizations such as bar charts, line charts, and heatmaps were implemented to help users explore patterns and make data-driven decisions. The dashboard is designed with a multi-page structure, separating key metrics and advanced analytics for better usability and clarity.*

""")

st.divider()

st.subheader("🚀 Navigate")
                  
st.page_link("Pages/Key_Metrics_Dashboard.py", label="📊 Key Metrics Dashboard")
st.page_link("Pages/Advanced_Stock_Analysis.py", label="📈Advanced Stock Analysis")
