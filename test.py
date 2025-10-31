import yfinance as yf

data = yf.Ticker("TCS.NS")
print(data.history(period="1mo"))
