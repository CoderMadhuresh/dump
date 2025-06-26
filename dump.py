import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

# ---------- SETTINGS ----------
capital = 100000  # ₹100,000 virtual capital
weights = {
    "INFY.NS": 0.3310,
    "TCS.NS": 0.3281
}
# ------------------------------

st.set_page_config(page_title="📊 Live Portfolio Tracker", layout="wide")
st.title("📈 Live Indian Stock Portfolio (Demo)")

# Function to get real-time prices
def get_current_prices(tickers):
    data = yf.download(tickers=list(tickers), period="1d", interval="1m", progress=False)
    prices = data['Close'].iloc[-1]
    return prices

# Virtual purchase
if "buy_prices" not in st.session_state:
    # Fetch real-time prices at the time of "buy"
    initial_prices = get_current_prices(weights.keys())
    st.session_state.buy_prices = initial_prices.to_dict()
    st.session_state.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Allocate shares at initial buy prices
def allocate_portfolio(buy_prices, weights, capital):
    allocations = []
    total_invested = 0
    for ticker in weights:
        allocated_money = capital * weights[ticker]
        price = buy_prices[ticker]
        quantity = int(allocated_money // price)
        invested = quantity * price
        total_invested += invested
        allocations.append({
            "Ticker": ticker,
            "Buy Price (₹)": round(price, 2),
            "Quantity": quantity,
            "Invested (₹)": round(invested, 2)
        })
    return pd.DataFrame(allocations), total_invested

# Compute live portfolio
def compute_current_value(df, live_prices):
    df["Live Price (₹)"] = df["Ticker"].apply(lambda x: round(live_prices[x], 2))
    df["Current Value (₹)"] = df["Quantity"] * df["Live Price (₹)"]
    df["P&L (₹)"] = df["Current Value (₹)"] - df["Invested (₹)"]
    df["P&L (%)"] = (df["P&L (₹)"] / df["Invested (₹)"]) * 100
    return df

# LIVE prices now
live_prices = get_current_prices(weights.keys())
alloc_df, invested_total = allocate_portfolio(st.session_state.buy_prices, weights, capital)
portfolio_df = compute_current_value(alloc_df, live_prices)

# Display Portfolio
st.markdown(f"🛒 Stocks bought at: `{st.session_state.timestamp}`")
st.metric("💰 Total Virtual Capital", f"₹{capital:,.0f}")
st.metric("📤 Invested", f"₹{invested_total:,.0f}")
st.metric("📈 Current Value", f"₹{portfolio_df['Current Value (₹)'].sum():,.0f}")
st.metric("📊 Total P&L", f"₹{portfolio_df['P&L (₹)'].sum():,.2f}",
          delta=f"{portfolio_df['P&L (%)'].mean():.2f}%")

st.dataframe(portfolio_df, use_container_width=True)

# Refresh Button
if st.button("🔁 Refresh Live Prices"):
    st.rerun()

st.caption("Live prices update every minute from Yahoo Finance. Click refresh to update.")
