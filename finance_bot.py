import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import ollama

# -------------------- Streamlit Page Config --------------------
st.set_page_config(page_title="AI Portfolio Generator", page_icon="💸", layout="centered")
st.title("💸 AI-Powered Indian Portfolio Advisor")

# -------------------- User Input Section --------------------
capital = st.number_input("💰 Initial Capital (₹)", min_value=1000, step=500)
monthly_investment = st.number_input("📆 Monthly Investment (₹)", min_value=500, step=100)
risk = st.selectbox("📊 Risk Appetite", ["Low", "Medium", "High"])
tools = st.multiselect("🏦 Preferred Investment Tools",
                       ["Mutual Funds", "Stocks", "Debt Funds", "Bonds", "ETFs"],
                       default=["Stocks", "Mutual Funds"])

st.markdown("---")

# -------------------- Fetch Stock Data Using yfinance --------------------
def get_stock_data(symbol, period="6mo"):
    try:
        data = yf.Ticker(symbol)
        hist = data.history(period=period)
        return hist
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()

# -------------------- RAG Component: Prepare Context --------------------
def prepare_context(symbols):
    context = ""
    for s in symbols:
        df = get_stock_data(s)
        if not df.empty:
            last_price = df["Close"].iloc[-1]
            avg_return = ((df["Close"].iloc[-1] - df["Close"].iloc[0]) / df["Close"].iloc[0]) * 100
            context += f"{s}: Last Price ₹{last_price:.2f}, 6M Return {avg_return:.2f}%\n"
    return context

# -------------------- Generate Portfolio with Mistral --------------------
def generate_portfolio(context, capital, monthly_investment, risk, tools):
    prompt = f"""
You are a financial advisor chatbot specialized for Indian investors.
Using the following market data and preferences, create a diversified investment portfolio.

Market Data:
{context}

User Info:
Initial Capital: ₹{capital}
Monthly Investment: ₹{monthly_investment}
Risk Appetite: {risk}
Preferred Tools: {', '.join(tools)}

Provide:
1. Allocation percentage for each tool (total 100%)
2. Example Indian stocks/mutual funds for each
3. Projected annual return estimate
4. Brief rationale behind each allocation
"""
    response = ollama.chat(model="mistral:7b", messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]

# -------------------- Streamlit Logic --------------------
if st.button("Generate Portfolio"):
    st.info("Fetching live data and generating recommendations... ⏳")

    # Use a few top NSE stocks for demonstration
    symbols = ["TCS.NS", "INFY.NS", "HDFCBANK.NS", "RELIANCE.NS", "ITC.NS"]

    context = prepare_context(symbols)
    result = generate_portfolio(context, capital, monthly_investment, risk, tools)

    st.success("✅ Portfolio Generated!")
    st.markdown(result)

    # -------------------- Visualization --------------------
    # Simple chart for stock trends
    st.markdown("### 📈 Example Stock Trends (Last 6 Months)")
    for sym in symbols[:3]:
        df = get_stock_data(sym)
        if not df.empty:
            fig, ax = plt.subplots()
            ax.plot(df.index, df["Close"])
            ax.set_title(sym)
            st.pyplot(fig)
