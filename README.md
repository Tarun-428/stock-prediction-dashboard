📈 Stock Prediction Dashboard

A full-stack stock analytics and prediction dashboard built with React, Flask, XGBoost, and yfinance, optimized for Indian stock market (NIFTY / BANKNIFTY / NSE stocks).

The application provides:

Real-time live stock price

TradingView-style candlestick chart

Historical price data

Technical indicators (SMA, RSI)

Machine Learning (XGBoost) prediction: UP/DOWN direction

Fundamentals

Dockerized frontend & backend

🚀 Features
🔹 1. Dashboard UI (React + ApexCharts)

TradingView-like candlestick chart

Volume bars

Timeframe filters: 1D, 5D, 1M, 3M, 6M, 1Y

Technical indicators (SMA5, SMA10, RSI14)

Fundamental insights

Modern UI (cards, color-coded predictions)

🔹 2. Backend API (Flask)

Backend provides:

Endpoint	Purpose
/stock-data	Historical OHLCV data + indicators + fundamentals
/predict	Short-term ML prediction using XGBoost
/live-price	Simple live price using yfinance
/health	Health check
🔹 3. Machine Learning Model

Uses XGBoost Classifier

Input: last 10 candles (OHLCV + SMA + RSI)

Output:

Direction → UP / DOWN

Confidence score

Suggested trade → BUY CALL / BUY PUT

🔹 4. Docker Support

1 container for backend

1 container for frontend

Managed using docker-compose

📁 Project Structure
StockApp/
│
├── backend/
│   ├── app.py
│   ├── predictor.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── ...
│
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   ├── api.js
│   │   ├── constants.js
│   │   ├── App.js
│   │   └── index.js
│   ├── package.json
│   ├── Dockerfile
│   └── ...
│
└── docker-compose.yml

🧠 ML Model Explanation (How It Works)
📌 Step 1: Data Collection

Fetch last 5 days of 15-minute candles using yfinance

Columns: Open, High, Low, Close, Volume

📌 Step 2: Feature Engineering

Add technical indicators:

SMA_5

SMA_10

RSI_14

📌 Step 3: Sliding Window Dataset

Each training sample is:

10-candle window → 10×8 features

Flattened to an 80-dimension vector

Label:

1 → price goes UP after 3 candles

0 → price goes DOWN

📌 Step 4: Model Training

Train an XGBoost classifier with:

300 trees

depth=5

learning_rate=0.05

subsample=0.9

colsample_bytree=0.9

📌 Step 5: Prediction

Take the most recent 10 candles

Predict UP or DOWN

Use probability as confidence

Estimate future price using heuristic:

future_price = live_price ± (0.01 * live_price * confidence%)

🛠 Installation (Local Setup)
1️⃣ Clone the repository
git clone https://github.com/<your-username>/stock-prediction-dashboard.git
cd stock-prediction-dashboard

🖥 Running Backend (Flask)
cd backend
pip install -r requirements.txt
python app.py


Backend runs at:

http://localhost:5000

🌐 Running Frontend (React)
cd frontend
npm install
npm start


Frontend runs at:

http://localhost:3000

🐳 Running with Docker (Recommended)

From the root folder:

docker compose up --build


docker direct pull images
docker pull tarunpatidar824/stock_price_prediction/stock-dashboard:backend

docker pull tarunpatidar824/stock_price_prediction/stock-dashboard:frontend

Frontend → http://localhost:3000

Backend → http://localhost:5000
