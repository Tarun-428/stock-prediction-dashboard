# predictor.py
import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier


def get_data(symbol: str, interval: str = "15m", days: int = 5) -> pd.DataFrame:
    """
    Download OHLCV data for given symbol and period using yfinance.
    """
    df = yf.download(
        tickers=symbol,
        interval=interval,
        period=f"{days}d",
        progress=False,
        auto_adjust=False,
    )
    if df.empty:
        raise ValueError(f"No data found for symbol: {symbol}")
    df.dropna(inplace=True)
    return df


def compute_rsi(series: pd.Series, period: int) -> pd.Series:
    """
    Compute Relative Strength Index (RSI) for a given price series.
    """
    delta = series.diff()

    gain = delta.where(delta > 0, 0.0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0.0).rolling(window=period).mean()

    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi


def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add technical indicators to the dataframe.
    """
    df = df.copy()
    df["SMA_5"] = df["Close"].rolling(5).mean()
    df["SMA_10"] = df["Close"].rolling(10).mean()
    df["RSI"] = compute_rsi(df["Close"], 14)

    df.dropna(inplace=True)
    return df


def prepare_data(
    df: pd.DataFrame, window_size: int = 10, prediction_offset: int = 3
):
    """
    Create windowed features X and labels y.
    Label = 1 if future close > current close, else 0.
    """
    X, y = [], []

    for i in range(len(df) - window_size - prediction_offset):
        window = df.iloc[i : i + window_size]
        future_price = df["Close"].iloc[i + window_size + prediction_offset].item()
        current_price = df["Close"].iloc[i + window_size].item()

        X.append(window.values)
        y.append(1 if future_price > current_price else 0)

    return np.array(X), np.array(y)


def train_model(X: np.ndarray, y: np.ndarray):
    """
    Train an XGBoost classifier on the provided features.
    NOTE: This retrains on each call for simplicity.
    """
    X = X.reshape(len(X), -1)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = XGBClassifier(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=5,
        subsample=0.9,
        colsample_bytree=0.9,
        n_jobs=-1,
        eval_metric="logloss",
    )
    model.fit(X_scaled, y)

    return model, scaler


def predict_direction(
    model: XGBClassifier, scaler: StandardScaler, features: pd.DataFrame, symbol: str
):
    """
    Use trained model to predict next direction and price band.
    """
    last_window = features.tail(10)
    latest = last_window.values.reshape(1, -1)
    scaled = scaler.transform(latest)

    pred = model.predict(scaled)[0]
    prob = model.predict_proba(scaled)[0]

    confidence = float(prob[pred] * 100.0)
    direction = "UP" if pred == 1 else "DOWN"
    suggestion = "BUY CALL" if pred == 1 else "BUY PUT"

    # Try to get live price
    live_price = None
    try:
        live_price = yf.Ticker(symbol).fast_info.get("lastPrice")
    except Exception:
        pass

    if live_price is None:
        live_price = float(features["Close"].iloc[-1])

    predicted_change = 0.01 * live_price * (confidence / 100.0)
    future_price = (
        live_price + predicted_change if pred == 1 else live_price - predicted_change
    )

    return {
        "symbol": symbol.upper(),
        "live_price": round(float(live_price), 2),
        "predicted_price": round(float(future_price), 2),
        "confidence": round(confidence, 2),
        "direction": direction,
        "suggestion": suggestion,
    }


def predict_stock(symbol: str):
    """
    High-level helper used by Flask endpoint.
    """
    raw = get_data(symbol)
    df_features = create_features(raw)

    features = df_features[
        ["Open", "High", "Low", "Close", "Volume", "SMA_5", "SMA_10", "RSI"]
    ]

    X, y = prepare_data(features)
    if len(X) == 0:
        raise ValueError("Not enough data to train the prediction model.")

    model, scaler = train_model(X, y)
    return predict_direction(model, scaler, features, symbol)
