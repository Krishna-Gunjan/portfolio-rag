# truedata_client.py
import os
import time
import json
import threading
import requests
from dotenv import load_dotenv
from cache import SimpleTTLCache

load_dotenv()

TRUEDATA_REST_API_KEY = os.getenv("TRUEDATA_REST_API_KEY")
TRUEDATA_REST_BASE = os.getenv("TRUEDATA_REST_BASE", "https://api.truedata.in")
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "300"))

cache = SimpleTTLCache()

def _rest_get(path, params=None):
    url = TRUEDATA_REST_BASE.rstrip("/") + "/" + path.lstrip("/")
    headers = {"Authorization": f"Bearer {TRUEDATA_REST_API_KEY}"} if TRUEDATA_REST_API_KEY else {}
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()

def get_stock_quote(symbol: str):
    """
    Fetch latest price for a symbol from TrueData REST (or cache).
    symbol: exchange-qualified string, e.g., 'RELIANCE.NSE' or 'RELIANCE.BSE' depending on provider.
    """
    cache_key = f"quote:{symbol}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    # Replace endpoint path and parsing logic with the TrueData REST spec.
    # This is a placeholder path (adjust to your TrueData plan).
    try:
        data = _rest_get("/v1/quote", params={"symbol": symbol})
    except Exception as e:
        # Fallback: return an error-laden placeholder or raise
        raise RuntimeError(f"TrueData REST error fetching {symbol}: {e}")

    # Expected data example: {"symbol":"RELIANCE.NSE","last": 2350.5, "change": 0.5, "timestamp": 169xxx}
    quote = {
        "symbol": data.get("symbol", symbol),
        "last": float(data.get("last", 0)),
        "change": data.get("change", None),
        "timestamp": int(data.get("timestamp", time.time()))
    }

    cache.set(cache_key, quote, CACHE_TTL_SECONDS)
    return quote

# Optional: WebSocket streaming (advanced)
# The WebSocket approach is efficient for high-frequency data but requires correct TrueData WS API.
# The following is a skeleton; enable and adapt to TrueData docs.

"""
import websocket

TRUEDATA_WS_URL = os.getenv("TRUEDATA_WS_URL", "wss://wstest.truedata.in")

def start_ws_stream(symbols, on_message_callback):
    def _on_message(ws, message):
        payload = json.loads(message)
        on_message_callback(payload)

    def _on_open(ws):
        # Example subscription message; replace per TrueData docs
        sub = {"action": "subscribe", "symbols": symbols, "token": TRUEDATA_REST_API_KEY}
        ws.send(json.dumps(sub))

    ws = websocket.WebSocketApp(TRUEDATA_WS_URL, on_message=_on_message, on_open=_on_open)
    thread = threading.Thread(target=ws.run_forever, daemon=True)
    thread.start()
    return ws
"""

# Helper for retrieving many quotes (batched)
def get_quotes(symbols):
    results = {}
    for s in symbols:
        try:
            results[s] = get_stock_quote(s)
        except Exception as e:
            results[s] = {"symbol": s, "error": str(e)}
    return results
