import time

import yfinance as yf
import plotly.graph_objs as go
import ccxt
import requests
import os

# ✅ FreeCurrencyAPI key
FREECURRENCY_API_KEY = "fca_live_uvpRZhgejJkX7iBvbaN3U14KKQkvEhEn4admRZ6o"

# 🔁 Stock tickers (Fetching only 2 stock charts)
STOCK_TICKERS = {
    "NIFTY 50": "^NSEI",
    "Bank NIFTY": "^NSEBANK",
    "Google": "GOOGL",
    "Apple": "AAPL",
    "Tesla": "TSLA",
    "Microsoft": "MSFT",
    "Amazon": "AMZN",
    "Reliance": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "HDFC Bank": "HDFCBANK.NS"
}

# 📈 Fetch intraday stock data (Only for the first 2 stocks)
def get_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period="1d", interval="5m")
        return data if not data.empty else None
    except Exception as e:
        print(f"Error fetching stock data for {ticker}: {e}")
        return None

# 📊 Generate candlestick chart with transparent background, no grids, and no titles
def generate_stock_chart(ticker, stock_name):
    data = get_stock_data(ticker)
    if data is None:
        return None

    try:
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data["Open"],
            high=data["High"],
            low=data["Low"],
            close=data["Close"],
            name=stock_name
        ))

        # Neutral colors for text and background
        background_color = 'rgba(0, 0, 0, 0)'  # Transparent background
        text_color = "#94a3b8"  # Neutral gray text color for visibility on both dark and light backgrounds
        grid_color = 'rgba(0, 0, 0, 0)'  # Transparent gridlines
        hover_background = 'rgba(0, 0, 0, 0.5)'  # Semi-transparent hover background color

        fig.update_layout(
            # Remove title, grids, and axis titles
            title=None,
            xaxis_title=None,
            yaxis_title=None,
            xaxis_rangeslider_visible=False,
            template="plotly_white",  # Use default white template for neutral colors
            margin=dict(l=0, r=0, t=0, b=0),
            autosize=True,
            dragmode=False,
            showlegend=False,
            plot_bgcolor=background_color,
            paper_bgcolor=background_color,
            font=dict(color=text_color),
            xaxis=dict(
                showgrid=False,  # Hide gridlines
                color=text_color
            ),
            yaxis=dict(
                showgrid=False,  # Hide gridlines
                color=text_color
            ),
            hovermode="closest",
            hoverlabel=dict(
                bgcolor=hover_background,  # Transparent background for hover labels
                font=dict(color=text_color),  # Neutral text color for hover labels
                bordercolor='rgba(0, 0, 0, 0)'  # Transparent border for hover labels
            )
        )

        # Optional: customize modebar (zoom, pan, etc.)
        config = {
            'displayModeBar': False,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['autoScale2d', 'resetScale2d']
        }

        return fig.to_html(full_html=False, config=config)
    except Exception as e:
        print(f"Error generating chart for {ticker}: {e}")
        return None

# 🪙 Fetch live crypto prices (No chart generation, only prices)
def get_crypto_data():
    crypto_prices = {}
    try:
        exchange = ccxt.binance()
        symbols = ["BTC/USDT", "ETH/USDT", "BNB/USDT", "ADA/USDT", "XRP/USDT"]

        for symbol in symbols:
            ticker = exchange.fetch_ticker(symbol)
            crypto_prices[symbol] = round(ticker['last'], 2)

    except Exception as e:
        print(f"Error fetching crypto data: {e}")
    return crypto_prices

# 💱 Fetch forex rates using FreeCurrencyAPI (No chart generation, only prices)
def get_forex_rates():
    forex_rates = {}
    pairs = {
        "USD/INR": ("USD", "INR"),
        "EUR/USD": ("EUR", "USD"),
        "GBP/USD": ("GBP", "USD"),
        "JPY/USD": ("JPY", "USD"),
        "AUD/USD": ("AUD", "USD"),
    }

    try:
        base_currencies = set(base for base, _ in pairs.values())
        for base in base_currencies:
            url = f"https://api.freecurrencyapi.com/v1/latest?apikey={FREECURRENCY_API_KEY}&base_currency={base}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if "data" in data:
                    for pair, (from_currency, to_currency) in pairs.items():
                        if from_currency == base and to_currency in data["data"]:
                            forex_rates[pair] = round(data["data"][to_currency], 4)
            else:
                print(f"Failed to fetch rates for base {base}: {response.status_code}")

    except Exception as e:
        print(f"Error fetching forex rates: {e}")

    return forex_rates

# 📰 Get live market news
def get_market_news():
    API_KEY = "wWldkWug1nD4yUTm7fsS4GY17LwDZ2RBmmo72Y3c"  # Use environment variable or the correct key
    url = f"https://api.marketaux.com/v1/news/all?api_token={API_KEY}&language=en&filter_entities=true&limit=6"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])
    except Exception as e:
        print(f"Error fetching market news: {e}")
        return []

# 🔍 Stock Search Function (Fetching only price and change)
def get_stock_info(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            'symbol': ticker.upper(),
            'name': info.get('shortName', 'N/A'),
            'price': round(info.get('regularMarketPrice', 0), 2),
            'change': round(info.get('regularMarketChangePercent', 0), 2)
        }
    except Exception as e:
        print(f"Error searching stock: {e}")
        return None

def search_stock(symbol):
    try:
        symbol = symbol.upper().strip()
        stock = yf.Ticker(symbol)

        # Try lightweight info first
        fast_info = stock.fast_info
        name = stock.info.get('longName') or stock.info.get('shortName') or 'N/A'

        return {
            'symbol': symbol,
            'name': name,
            'price': round(fast_info.get('lastPrice', 0), 2),
            'change': round(stock.info.get('regularMarketChangePercent', 0), 2),
            'currency': fast_info.get('currency') or stock.info.get('currency', 'USD'),
            'exchange': stock.info.get('exchange', 'N/A'),
            'market_cap': stock.info.get('marketCap', None),
        }
    except Exception as e:
        print(f"❌ Error searching stock '{symbol}': {e}")
        return {
            'symbol': symbol,
            'name': 'Not Found',
            'price': 0.0,
            'change': 0.0,
            'currency': 'USD',
            'exchange': 'N/A',
            'market_cap': None,
        }

ALPHA_VANTAGE_API_KEY="2F3L1C6904O4DDHC"

import time
import requests
import yfinance as yf

HEADERS = {
    "User-Agent": "Mozilla/5.0",
}

def dynamic_search_stock(query):
    """
    Try to find stock data by company name or ticker symbol.
    Handles Yahoo Finance rate limits and fallbacks.
    """
    try:
        query = query.strip()
        if not query:
            print("[Warning] Empty query.")
            return []

        # Try resolving symbols first
        symbols = resolve_symbol_from_name(query)
        if symbols:
            results = []
            for symbol_data in symbols:
                symbol = symbol_data['symbol']
                # Fetch stock details for each resolved symbol
                stock_details = fetch_stock_details(symbol)
                if stock_details:
                    stock_details[0]['quote_type'] = symbol_data['quote_type']  # Add quote type to the result
                    results.append(stock_details[0])
            return results

        # Fall back to using the query as a ticker directly
        return fetch_stock_details(query)

    except Exception as e:
        print(f"[Fatal Error] While searching stock '{query}': {e}")
        return []

def resolve_symbol_from_name(name):
    """
    Resolve a symbol from company name using Yahoo Finance autocomplete.
    Fetch multiple quote types (e.g., stock, ETF, crypto, etc.).
    """
    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={name}"
        response = requests.get(url, headers=HEADERS, timeout=5)

        if response.status_code == 429:
            print(f"[Rate Limit] Too many requests for name '{name}'. Retrying after delay...")
            time.sleep(2)
            return resolve_symbol_from_name(name)

        response.raise_for_status()
        data = response.json()

        results = []
        for match in data.get("quotes", []):
            quote_type = match.get("quoteType")
            symbol = match.get("symbol")

            # Include a range of quote types like stock, ETF, etc.
            if symbol and quote_type in ["EQUITY", "ETF", "MUTUALFUND", "INDEX", "CURRENCY", "CRYPTO", "FUTURE", "OPTION", "BOND", "REIT"]:
                results.append({
                    'symbol': symbol,
                    'quote_type': quote_type
                })

        if not results:
            print(f"[Info] No matching symbols found for '{name}'")
        return results

    except Exception as e:
        print(f"[Error] Failed to resolve symbols for '{name}': {e}")
        return []

def fetch_stock_details(symbol):
    """
    Fetch stock info for a given valid symbol using yfinance.
    """
    try:
        stock = yf.Ticker(symbol)
        info = stock.info

        if not info or "regularMarketPrice" not in info:
            print(f"[Info] No valid market price for symbol '{symbol}'")
            return []

        return [{
            'symbol': info.get('symbol', symbol),
            'name': info.get('shortName') or info.get('longName', 'N/A'),
            'price': round(info.get('regularMarketPrice', 0.0), 2),
            'change': round(info.get('regularMarketChangePercent', 0.0), 2),
            'currency': info.get('currency', 'USD'),
            'exchange': info.get('exchange', 'N/A'),
            'market_cap': info.get('marketCap', 'N/A'),
            'previous_close': info.get('previousClose', 'N/A'),
            'open': info.get('open', 'N/A'),
            'high': info.get('dayHigh', 'N/A'),
            'low': info.get('dayLow', 'N/A'),
            'year_high': info.get('fiftyTwoWeekHigh', 'N/A'),
            'year_low': info.get('fiftyTwoWeekLow', 'N/A'),
        }]
    except Exception as e:
        print(f"[Error] Failed to fetch stock data for symbol '{symbol}': {e}")
        return []
