from flask import Flask, request, jsonify
import yfinance as yf
from flask_cors import CORS
from datetime import datetime, timedelta
from predictor import predict_stock
import traceback
import pytz
import pandas as pd

app = Flask(__name__)
CORS(app)

IST = pytz.timezone("Asia/Kolkata")

@app.route('/stock-data', methods=['GET'])
def get_stock_data():
    symbol = request.args.get('symbol')
    start = request.args.get('start')
    end = request.args.get('end')

    if not symbol or not start or not end:
        return jsonify({"error": "Missing parameters"}), 400

    try:
        print(f"[INFO] Fetching stock data for {symbol} from {start} to {end}")

        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d") + timedelta(days=1)

        interval = '1m' if (datetime.now() - start_date).days <= 7 else '1d'

        df = yf.download(
            symbol,
            start=start_date,
            end=end_date,
            interval=interval,
            auto_adjust=False,
            progress=False
        )

        if df.empty:
            print("[WARNING] No data found.")
            return jsonify({"error": "No data found."}), 404

        df.reset_index(inplace=True)
        # Step: Convert timezone to IST

        # Flatten multi-level columns if any (like ('Open', ''))
        df.columns = df.columns.map(lambda x: x[0] if isinstance(x, tuple) else x)

        # Ensure 'Date' column exists
        if 'Datetime' in df.columns:
            df.rename(columns={'Datetime': 'Date'}, inplace=True)

        df = df.sort_values(by='Date')

        # Convert to IST timezone if needed
        IST = pytz.timezone("Asia/Kolkata")
        if df['Date'].dt.tz is None:
            df['Date'] = df['Date'].dt.tz_localize('UTC').dt.tz_convert(IST)
        else:
            df['Date'] = df['Date'].dt.tz_convert(IST)

        # Prepare chart data
        chart_data = {
            "dates": df['Date'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist(),
            "open": df['Open'].fillna(0).round(2).tolist(),
            "high": df['High'].fillna(0).round(2).tolist(),
            "low": df['Low'].fillna(0).round(2).tolist(),
            "close": df['Close'].fillna(0).round(2).tolist(),
            "volume": df['Volume'].fillna(0).astype(int).tolist()
        }


        # Pricing Table
        pricing_df = df.copy()
        if 'Adj Close' not in pricing_df.columns:
            pricing_df['Adj Close'] = pricing_df['Close']

        pricing_df['% Change'] = pricing_df['Adj Close'].pct_change().fillna(0) * 100
        pricing_df['Date'] = pricing_df['Date'].astype(str)

        pricing_json = pricing_df[[
            'Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', '% Change'
        ]].round(2).iloc[::-1].to_dict(orient='records')

        # Fundamental Data
        ticker_obj = yf.Ticker(symbol)
        info = ticker_obj.info

        fundamentals = {
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "marketCap": info.get("marketCap"),
            "trailingPE": info.get("trailingPE"),
            "forwardPE": info.get("forwardPE"),
            "epsTrailingTwelveMonths": info.get("epsTrailingTwelveMonths"),
            "dividendYield": info.get("dividendYield"),
            "beta": info.get("beta")
        }

        return jsonify({
            "chartData": chart_data,
            "pricing": pricing_json,
            "fundamentals": fundamentals
        })

    except Exception as e:
        print("[ERROR] Exception in /stock-data:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/predict', methods=['GET'])
def predict():
    symbol = request.args.get('symbol')
    try:
        print(f"[INFO] Generating prediction for {symbol}")
        result = predict_stock(symbol)
        return jsonify(result)
    except Exception as e:
        print("[ERROR] Prediction failed:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)