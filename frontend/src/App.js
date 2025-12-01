// src/App.js
import React, { useState, useEffect } from "react";
import "./App.css";
import Controls from "./components/Controls";
import PriceChart from "./components/PriceChart";
import PricingTable from "./components/PricingTable";
import Sidebar from "./components/Sidebar";
import { TIMEFRAMES } from "./constants";
import { getStockData, getPrediction, getLivePrice } from "./api";

function formatDate(date) {
  const d = new Date(date);
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

function App() {
  const [symbol, setSymbol] = useState("NIFTY");
  const [timeframe, setTimeframe] = useState(TIMEFRAMES[1]); // 5D default
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  const [chartData, setChartData] = useState(null);
  const [pricing, setPricing] = useState([]);
  const [fundamentals, setFundamentals] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [prediction, setPrediction] = useState(null);
  const [predictionLoading, setPredictionLoading] = useState(false);

  const [livePrice, setLivePrice] = useState(null);
  const [liveTime, setLiveTime] = useState(null);
  const [liveError, setLiveError] = useState("");

  // init start/end from default timeframe
useEffect(() => {
  const now = new Date();
  const end = formatDate(now);
  const start = formatDate(
    new Date(now.getTime() - timeframe.days * 24 * 60 * 60 * 1000)
  );

  setStartDate(start);
  setEndDate(end);
}, [timeframe.days]);   // ✅ Fix warning


  // Poll live price from /live-price
  useEffect(() => {
    if (!symbol) return;

    const fetchLive = async () => {
      try {
        const data = await getLivePrice(symbol);
        setLivePrice(data.price);
        setLiveTime(new Date().toLocaleTimeString("en-IN"));
        setLiveError("");
      } catch (err) {
        setLiveError(
          err.response?.data?.error || "Unable to fetch live price."
        );
      }
    };

    fetchLive();
    const id = setInterval(fetchLive, 7000);
    return () => clearInterval(id);
  }, [symbol]);

  const applyTimeframe = (tf) => {
    const now = new Date();
    const end = formatDate(now);
    const start = formatDate(
      new Date(now.getTime() - tf.days * 24 * 60 * 60 * 1000)
    );
    setTimeframe(tf);
    setStartDate(start);
    setEndDate(end);
  };

  const handleLoadData = async () => {
    if (!symbol || !startDate || !endDate) return;
    try {
      setLoading(true);
      setError("");

      const data = await getStockData(symbol, startDate, endDate);

      setChartData(data.chartData);
      setPricing(data.pricing || []);
      setFundamentals(data.fundamentals || null);
    } catch (err) {
      console.error(err);
      const msg =
        err.response?.data?.error || "Failed to fetch stock data from server.";
      setError(msg);
      setChartData(null);
      setPricing([]);
      setFundamentals(null);
    } finally {
      setLoading(false);
    }
  };

  const handlePredict = async () => {
    if (!symbol) return;
    try {
      setPredictionLoading(true);
      setPrediction(null);

      const data = await getPrediction(symbol);
      setPrediction(data);
    } catch (err) {
      console.error(err);
      setPrediction({
        error:
          err.response?.data?.error || "Prediction failed. Try again later.",
      });
    } finally {
      setPredictionLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="navbar">
        <div className="nav-left">
          <h1>Indian Stock Dashboard</h1>
          <span className="nav-subtitle">
            NIFTY / BANKNIFTY / NSE stocks (Flask + React)
          </span>
        </div>
      </header>

      <main className="content">
        <section className="left-panel">
          <Controls
            symbol={symbol}
            startDate={startDate}
            endDate={endDate}
            timeframe={timeframe}
            loading={loading}
            onSymbolChange={setSymbol}
            onStartDateChange={setStartDate}
            onEndDateChange={setEndDate}
            onTimeframeChange={applyTimeframe}
            onLoadClick={handleLoadData}
          />

          {error && <div className="card error-card">{error}</div>}

          <PriceChart
            symbol={symbol}
            timeframe={timeframe}
            chartData={chartData}
          />

          <PricingTable pricing={pricing} />
        </section>

        <Sidebar
          symbol={symbol}
          livePrice={livePrice}
          liveTime={liveTime}
          liveError={liveError}
          fundamentals={fundamentals}
          prediction={prediction}
          predictionLoading={predictionLoading}
          onPredictClick={handlePredict}
        />
      </main>
    </div>
  );
}

export default App;
