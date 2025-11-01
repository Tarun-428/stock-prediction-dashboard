# 📈 Stock Prediction Dashboard

An interactive **Stock Prediction Dashboard** that uses **Machine Learning (XGBoost)** to forecast stock prices and visualize performance through an elegant **React** frontend.
The project combines a **Flask backend** for model serving and API integration with a **React frontend** for data visualization using **React Charts**.

---

## 🧩 Project Overview

This project enables users to:

* Fetch and analyze historical stock price data.
* Predict future stock prices using an XGBoost regression model.
* Visualize stock performance through dynamic, responsive charts.
* Interact with prediction windows (1-day, 7-day, 30-day, etc.).
* View all analytics in a sleek, web-based dashboard.

---

## 🗂️ Project Structure

```
stock-prediction-dashboard/
│
├── backend/                 # Flask API & ML Model
│   ├── app.py               # Main Flask application
│   ├── model/               # Trained XGBoost model files
│   ├── utils/               # Data preprocessing, feature engineering
│   ├── requirements.txt     # Python dependencies
│   └── ...
│
├── frontend/                # React application
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # Dashboard pages
│   │   ├── charts/          # Chart components using React Charts
│   │   └── App.js
│   ├── package.json
│   └── ...
│
└── README.md
```

---

## ⚙️ Tech Stack

### **Backend**

* **Python 3.x**
* **Flask** — RESTful API for model interaction
* **XGBoost** — core ML algorithm for stock price prediction
* **Pandas, NumPy, Scikit-learn** — data processing and feature engineering
* **YFinance / AlphaVantage API** — fetching historical stock data

### **Frontend**

* **React.js**
* **React Charts / Chart.js** — data visualization
* **Axios** — API communication
* **Bootstrap / Material UI** — styling and layout

---

## 🚀 Getting Started

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Tarun-428/stock-prediction-dashboard.git
cd stock-prediction-dashboard
```

---

### 2️⃣ Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate      # on Windows
# source venv/bin/activate  # on macOS/Linux

pip install -r requirements.txt
```

#### Run the Flask Server:

```bash
python app.py
```

By default, the server runs at:

```
http://127.0.0.1:5000
```

---

### 3️⃣ Frontend Setup

```bash
cd ../frontend
npm install
npm start
```

The React app will start at:

```
http://localhost:3000
```

Make sure the backend is running before using the frontend.

---

## 🔄 How It Works

1. **User selects a stock** (e.g., AAPL, TSLA, MSFT) and prediction window.
2. **Flask backend** fetches historical data and feeds it into the **XGBoost model**.
3. The model outputs predicted prices for the selected time horizon.
4. **React frontend** receives data via API and renders:

   * Interactive line charts for actual vs predicted values.
   * Statistical summaries and accuracy metrics.
   * Dynamic visual transitions for different time windows.

---

## 🧠 Machine Learning Details

* **Model:** XGBoost Regressor
* **Features:** historical prices, moving averages, volume, technical indicators (RSI, EMA, etc.)
* **Target:** next-day closing price or window-based forecast
* **Training:** optimized using grid search / cross-validation
* **Evaluation Metrics:** RMSE, MAE, R²

---

## 📊 Frontend Visualizations

* **Line Chart** — Historical vs Predicted stock price
* **Bar Chart** — Daily returns comparison
* **Card Stats** — Accuracy, trend indicators, latest prediction
* **Selector** — Change prediction window dynamically

---

## 🌐 Deployment

### Option 1 — Combined Deployment

* Build React frontend:

  ```bash
  npm run build
  ```
* Serve build files through Flask:

  ```python
  from flask import Flask, send_from_directory

  app = Flask(__name__, static_folder="../frontend/build", static_url_path="/")

  @app.route("/")
  def index():
      return send_from_directory(app.static_folder, "index.html")
  ```

### Option 2 — Separate Deployment

* Host **frontend** (React build) on Netlify or Vercel.
* Deploy **backend** (Flask) on Render, Railway, or AWS EC2.
* Update API base URLs in frontend `.env` to point to backend host.

---

## 🧾 Example API Endpoints

| Endpoint          | Method | Description                                              |
| ----------------- | ------ | -------------------------------------------------------- |
| `/api/predict`    | POST   | Returns predicted stock prices for given symbol & window |
| `/api/stock-data` | GET    | Fetches historical data for a given ticker               |
| `/api/health`     | GET    | Health check endpoint for backend                        |

---

## 🧰 Environment Variables

| Variable       | Description                           |
| -------------- | ------------------------------------- |
| `API_KEY`      | Stock data API key (if required)      |
| `MODEL_PATH`   | Path to saved XGBoost model           |
| `CORS_ORIGINS` | Allowed origins for frontend requests |

Create a `.env` file in your backend folder to manage these.

---

## 🤝 Contributing

Pull requests and contributions are welcome!

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

---

## 📜 License

This project is licensed under the **MIT License**.
See the [LICENSE](LICENSE) file for details.

---
