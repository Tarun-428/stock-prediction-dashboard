import yfinance as yf
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

def get_data(symbol, interval='15m', days=5):
    data = yf.download(tickers=symbol, interval=interval, period=f"{days}d",
                       progress=False, auto_adjust=False)
    if data.empty:
        raise Exception(f"No data found for symbol: {symbol}")
    data.dropna(inplace=True)
    return data

def compute_rsi(series, period):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def create_features(data):
    data['SMA_5'] = data['Close'].rolling(5).mean()
    data['SMA_10'] = data['Close'].rolling(10).mean()
    data['RSI'] = compute_rsi(data['Close'], 14)
    data.dropna(inplace=True)
    return data

def prepare_data(data, window_size=10, prediction_offset=3):
    X, y = [], []
    for i in range(len(data) - window_size - prediction_offset):
        window = data.iloc[i:i+window_size]
        future_price = data['Close'].iloc[i + window_size + prediction_offset].item()
        current_price = data['Close'].iloc[i + window_size].item()
        label = 1 if future_price > current_price else 0
        X.append(window.values)
        y.append(label)
    return np.array(X), np.array(y)

def train_model(X, y):
    X = X.reshape(len(X), -1)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    model = XGBClassifier(n_estimators=300, learning_rate=0.05, max_depth=5)
    model.fit(X_scaled, y)
    return model, scaler

def predict_direction(model, scaler, latest_data, symbol):
    features = latest_data[-10:]
    latest = features.values.reshape(1, -1)
    scaled = scaler.transform(latest)
    pred = model.predict(scaled)[0]
    prob = model.predict_proba(scaled)[0]
    confidence = prob[pred] * 100
    direction = "UP" if pred == 1 else "DOWN"
    suggestion = "BUY CALL" if pred == 1 else "BUY PUT"
    try:
        live_price = yf.Ticker(symbol).fast_info.get("lastPrice")
        if live_price is None:
            raise ValueError
    except:
        live_price = latest_data['Close'].iloc[-1].item()
    predicted_change = 0.01 * live_price * (confidence / 100)
    future_price = live_price + predicted_change if pred == 1 else live_price - predicted_change
    return {
        "symbol": symbol,
        "live_price": round(float(live_price), 2),
        "predicted_price": round(float(future_price), 2),
        "confidence": round(float(confidence), 2),
        "direction": direction,
        "suggestion": suggestion
    }

def predict_stock(symbol):
    data = get_data(symbol)
    data = create_features(data)
    features = data[['Open','High','Low','Close','Volume','SMA_5','SMA_10','RSI']]
    X, y = prepare_data(features)
    if len(X) == 0:
        raise Exception("Not enough data to predict.")
    model, scaler = train_model(X, y)
    return predict_direction(model, scaler, features, symbol)

