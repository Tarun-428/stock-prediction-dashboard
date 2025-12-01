# app.py
from datetime import datetime, timedelta

import pandas as pd
import pytz
import traceback
import yfinance as yf
from flask import Flask, request, jsonify
from flask_cors import CORS

from predictor import predict_stock

app = Flask(__name__)
CORS(app)

IST = pytz.timezone("Asia/Kolkata")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "api"}), 200


@app.route("/stock-data", methods=["GET"])
def get_stock_data():
    """
    Query params:
      - symbol: e.g. RELIANCE, TCS, NIFTY, BANKNIFTY, SENSEX, ITC.NS, etc.
      - start:  YYYY-MM-DD (IST)
      - end:    YYYY-MM-DD (IST)

    Returns:
      - chartData: { dates, open, high, low, close, volume }
      - pricing:   list of OHLC rows
      - fundamentals: basic info from yfinance
    """
    raw_symbol = request.args.get("symbol")
    start = request.args.get("start")
    end = request.args.get("end")

    if not raw_symbol or not start or not end:
        return jsonify({"error": "Missing parameters: symbol, start, end are required."}), 400

    # Map Indian-style names to Yahoo tickers
    symbol = normalize_symbol_for_india(raw_symbol)

    try:
        print(f"[INFO] Fetching stock data for {raw_symbol} -> {symbol} from {start} to {end}")

        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d") + timedelta(days=1)

        # Days between start and end (not today-based now)
        days_range = (end_date - start_date).days

        # For Indian market:
        # - <= 5 days: intraday (5m / 15m / 30m)
        # - <= 60 days: coarser intraday
        # - > 60 days: daily data
        if days_range <= 5:
            interval_candidates = ["5m", "15m", "30m", "1d"]
        elif days_range <= 60:
            interval_candidates = ["15m", "30m", "1d"]
        else:
            interval_candidates = ["1d"]

        df = None
        used_interval = None

        for interval in interval_candidates:
            print(f"[INFO] Trying interval={interval}")
            tmp = yf.download(
                symbol,
                start=start_date,
                end=end_date,
                interval=interval,
                auto_adjust=False,
                progress=False,
            )

            if not tmp.empty:
                df = tmp
                used_interval = interval
                break

        if df is None or df.empty:
            print("[WARNING] No data found for any interval.")
            return jsonify({
                "error": (
                    "No price data available for this symbol/date range. "
                    "Check if the market was open on these dates and the symbol is valid "
                    "for NSE/BSE (e.g. RELIANCE, TCS, HDFCBANK, NIFTY, BANKNIFTY, SENSEX, etc.)."
                )
            }), 404

        print(f"[INFO] Using interval: {used_interval}")

        # Reset index so Date/Datetime becomes a column
        df = df.reset_index()

        # Flatten multi-index columns if any
        df.columns = df.columns.map(lambda x: x[0] if isinstance(x, tuple) else x)

        # Normalize datetime column name to 'Date'
        if "Datetime" in df.columns:
            df = df.rename(columns={"Datetime": "Date"})
        elif "Date" not in df.columns:
            df.rename(columns={df.columns[0]: "Date"}, inplace=True)

        # Sort by date
        df = df.sort_values(by="Date")
        
        max_points = 1000  # or 800/500 as you like
        if len(df) > max_points:
            step = len(df) // max_points + 1
            df = df.iloc[::step].copy()
            print(f"[INFO] Downsampled server data to {len(df)} points")

        # Ensure timezone is IST
        if pd.api.types.is_datetime64_any_dtype(df["Date"]):
            if df["Date"].dt.tz is None:
                df["Date"] = df["Date"].dt.tz_localize("UTC").dt.tz_convert(IST)
            else:
                df["Date"] = df["Date"].dt.tz_convert(IST)
        else:
            df["Date"] = pd.to_datetime(df["Date"], utc=True).dt.tz_convert(IST)

        # Chart data
        chart_data = {
            "dates": df["Date"].dt.strftime("%Y-%m-%d %H:%M:%S").tolist(),
            "open": df["Open"].fillna(0).round(2).tolist(),
            "high": df["High"].fillna(0).round(2).tolist(),
            "low": df["Low"].fillna(0).round(2).tolist(),
            "close": df["Close"].fillna(0).round(2).tolist(),
            "volume": df["Volume"].fillna(0).astype(int).tolist(),
        }

        # Pricing table
        pricing_df = df.copy()
        if "Adj Close" not in pricing_df.columns:
            pricing_df["Adj Close"] = pricing_df["Close"]

        pricing_df["% Change"] = (
            pricing_df["Adj Close"].pct_change().fillna(0) * 100
        )
        pricing_df["Date"] = pricing_df["Date"].astype(str)

        pricing_json = (
            pricing_df[
                ["Date", "Open", "High", "Low", "Close", "Adj Close", "Volume", "% Change"]
            ]
            .round(2)
            .iloc[::-1]  # latest first
            .to_dict(orient="records")
        )

        # Fundamentals (works for many Indian tickers as well)
        ticker_obj = yf.Ticker(symbol)
        try:
            info = ticker_obj.info
        except Exception as e:
            print("[WARNING] Could not fetch fundamentals:", e)
            info = {}

        fundamentals = {
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "marketCap": info.get("marketCap"),
            "trailingPE": info.get("trailingPE"),
            "forwardPE": info.get("forwardPE"),
            "epsTrailingTwelveMonths": info.get("epsTrailingTwelveMonths"),
            "dividendYield": info.get("dividendYield"),
            "beta": info.get("beta"),
        }

        return jsonify(
            {
                "chartData": chart_data,
                "pricing": pricing_json,
                "fundamentals": fundamentals,
            }
        )

    except Exception as e:
        print("[ERROR] Exception in /stock-data:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/predict", methods=["GET"])
def predict():
    """
    Predict direction for a symbol using XGBoost.

    Query params:
      - symbol (Indian style allowed: RELIANCE, TCS, NIFTY, BANKNIFTY, SENSEX, etc.)
    """
    raw_symbol = request.args.get("symbol")
    if not raw_symbol:
        return jsonify({"error": "symbol query parameter is required"}), 400

    # Map Indian-style name to Yahoo Finance ticker
    symbol = normalize_symbol_for_india(raw_symbol)

    try:
        print(f"[INFO] Generating prediction for {raw_symbol} -> {symbol}")
        result = predict_stock(symbol)

        # Show the original symbol back to frontend (nicer UX)
        result["symbol"] = raw_symbol.upper()

        return jsonify(result)
    except ValueError as e:
        # Our predictor raises ValueError("No data found for symbol...")
        print("[ERROR] Prediction failed (no data):", e)
        return jsonify({
            "error": (
                "No enough data available to make a prediction for this symbol. "
                "Check if the symbol is valid for NSE/BSE (e.g. RELIANCE, TCS, HDFCBANK, "
                "NIFTY, BANKNIFTY, SENSEX) and the market has traded recently."
            )
        }), 404
    except Exception as e:
        print("[ERROR] Prediction failed:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def normalize_symbol_for_india(symbol: str) -> str:
    """
    Convert user-friendly Indian symbols into Yahoo Finance tickers.

    Examples:
      NIFTY      -> ^NSEI
      NIFTY50    -> ^NSEI
      BANKNIFTY  -> ^NSEBANK
      SENSEX     -> ^BSESN
      RELIANCE   -> RELIANCE.NS
      TCS        -> TCS.NS
      ITC.NS     -> ITC.NS (unchanged)
      ^NSEI      -> ^NSEI (unchanged)
    """
    if not symbol:
        return symbol

    s = symbol.strip().upper()

    index_aliases = {
        "NIFTY": "^NSEI",
        "NIFTY50": "^NSEI",
        "NIFTY_50": "^NSEI",
        "NIFTY 50": "^NSEI",
        "BANKNIFTY": "^NSEBANK",
        "NIFTYBANK": "^NSEBANK",
        "NIFTY_BANK": "^NSEBANK",
        "NIFTY BANK": "^NSEBANK",
        "SENSEX": "^BSESN",
    }

    # If it's a known index alias, map directly
    if s in index_aliases:
        return index_aliases[s]

    # If user already passed a Yahoo-style ticker, keep it
    if s.endswith(".NS") or s.endswith(".BO") or s.startswith("^"):
        return s

    # Default: treat it as an NSE stock
    return s + ".NS"

@app.route("/live-price", methods=["GET"])
def live_price():
    """
    Simple live price endpoint for Indian symbols.
    Query:
      - symbol: RELIANCE, TCS, NIFTY, BANKNIFTY, etc.
    Uses normalize_symbol_for_india + yfinance.fast_info.
    """
    raw_symbol = request.args.get("symbol")
    if not raw_symbol:
        return jsonify({"error": "symbol query parameter is required"}), 400

    symbol = normalize_symbol_for_india(raw_symbol)
    try:
        t = yf.Ticker(symbol)
        last = t.fast_info.get("lastPrice")
        if last is None:
            # fallback: last close
            hist = t.history(period="1d")
            if not hist.empty:
                last = float(hist["Close"].iloc[-1])

        if last is None:
            return jsonify({"error": f"No live price for {raw_symbol}"}), 404

        return jsonify({
            "symbol": raw_symbol.upper(),
            "price": round(float(last), 2),
        })
    except Exception as e:
        print("[ERROR] /live-price failed:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Runs on port 5000
    app.run(host="0.0.0.0", port=5000, debug=True)
