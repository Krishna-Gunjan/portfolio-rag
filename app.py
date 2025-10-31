# app.py
import streamlit as st
import json
from dotenv import load_dotenv
import os
from truedata_client import get_quotes, get_stock_quote
from llm_client import generate_from_ollama
from utils import build_prompt

load_dotenv()

st.set_page_config(page_title="Portfolio RAG - Indian Advisor", layout="wide")

st.title("AI Portfolio Advisor (RAG) — India 🇮🇳")
st.markdown("""
Enter investor details and preferences. The system retrieves live market data (TrueData)
and generates a recommended portfolio using Mistral:7B (Ollama).  
**Note:** This is a demo. Not financial advice.
""")

with st.sidebar:
    st.header("Investor Inputs")
    capital = st.number_input("Lump-sum capital (INR)", min_value=0.0, value=50000.0, step=1000.0)
    monthly = st.number_input("Monthly SIP (INR)", min_value=0.0, value=2000.0, step=500.0)
    preferred = st.multiselect("Preferred instruments", ["mutual funds", "stocks", "bonds", "debt funds", "etf"], default=["mutual funds", "stocks"])
    risk = st.selectbox("Risk appetite", ["low", "medium", "high"])
    horizon_years = st.slider("Investment horizon (years)", min_value=1, max_value=30, value=5)

    st.markdown("---")
    st.markdown("Quick symbol picks (example):")
    symbols_text = st.text_area("Stock symbols (comma-separated, exchange-qualified)", value="RELIANCE.NSE,HDFCBANK.NSE,INFY.NSE")
    symbols = [s.strip() for s in symbols_text.split(",") if s.strip()]

if st.button("Generate Recommendation"):
    st.info("Fetching market data...")
    # Retrieve market data (TrueData)
    try:
        market_data = get_quotes(symbols)
    except Exception as e:
        st.error(f"Error fetching market data: {e}")
        market_data = {s: {"error": str(e)} for s in symbols}

    st.success("Market data fetched (from TrueData / cache).")
    st.write(market_data)

    user_input = {
        "capital": capital,
        "monthly": monthly,
        "preferred": preferred,
        "risk": risk,
        "horizon_years": horizon_years,
        "symbols_sample": symbols
    }

    prompt = build_prompt(user_input, market_data)
    st.code(prompt[:1000] + ("...\n[truncated]" if len(prompt) > 1000 else ""), language="text")

    st.info("Generating recommendation from Mistral via Ollama...")
    try:
        raw = generate_from_ollama(prompt, max_tokens=1024, temperature=0.1)
        st.success("Received response from model.")
    except Exception as e:
        st.error(f"LLM generation error: {e}")
        raw = None

    # Try parse JSON
    parsed = None
    if raw:
        # Some models return extra text; find first JSON object in the string
        try:
            start = raw.find("{")
            end = raw.rfind("}") + 1
            json_text = raw[start:end]
            parsed = json.loads(json_text)
        except Exception as e:
            st.error(f"Error parsing JSON from model output: {e}")
            st.subheader("Raw model output")
            st.text(raw)

    if parsed:
        st.subheader("Portfolio Recommendation (Parsed JSON)")
        st.json(parsed)
        # Display allocation as cards
        st.subheader("Allocation")
        cols = st.columns(len(parsed.get("allocation", [])) or 1)
        for i, alloc in enumerate(parsed.get("allocation", [])):
            col = cols[i % len(cols)]
            with col:
                st.markdown(f"### {alloc.get('category')} — {alloc.get('percent')}%")
                st.write("Instruments:")
                for instr in alloc.get("instruments", []):
                    st.write(f"- {instr}")
                if "note" in alloc:
                    st.info(alloc["note"])

        st.subheader("Projected return")
        st.metric("Estimated annualized return (CAGR)", f"{parsed.get('projected_return')}%")
        st.write("Assumptions")
        for a in parsed.get("assumptions", []):
            st.write(f"- {a}")
        st.write("Explanation")
        st.write(parsed.get("explanation", ""))

    st.balloons()
