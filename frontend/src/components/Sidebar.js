// src/components/Sidebar.js
import React from "react";

function Sidebar({
  symbol,
  livePrice,
  liveTime,
  liveError,
  fundamentals,
  prediction,
  predictionLoading,
  onPredictClick,
}) {
  return (
    <section className="right-panel">
      {/* Live Price */}
      <div className="card info-card">
        <h2>Live Price</h2>
        {livePrice ? (
          <>
            <div className="live-price">
              {symbol}: <span>₹{livePrice.toFixed(2)}</span>
            </div>
            {liveTime && (
              <div className="live-time">Last update: {liveTime}</div>
            )}
          </>
        ) : (
          <div className="muted">
            {liveError || "Waiting for live data..."}
          </div>
        )}
      </div>

      {/* Fundamentals */}
      <div className="card info-card">
        <h2>Fundamentals</h2>
        {fundamentals ? (
          <ul className="fundamentals-list">
            <li>
              <span>Sector:</span> {fundamentals.sector || "N/A"}
            </li>
            <li>
              <span>Industry:</span> {fundamentals.industry || "N/A"}
            </li>
            <li>
              <span>Market Cap:</span>{" "}
              {fundamentals.marketCap
                ? fundamentals.marketCap.toLocaleString()
                : "N/A"}
            </li>
            <li>
              <span>Trailing PE:</span> {fundamentals.trailingPE ?? "N/A"}
            </li>
            <li>
              <span>Forward PE:</span> {fundamentals.forwardPE ?? "N/A"}
            </li>
            <li>
              <span>EPS (TTM):</span>{" "}
              {fundamentals.epsTrailingTwelveMonths ?? "N/A"}
            </li>
            <li>
              <span>Dividend Yield:</span>{" "}
              {fundamentals.dividendYield
                ? (fundamentals.dividendYield * 100).toFixed(2) + "%"
                : "N/A"}
            </li>
            <li>
              <span>Beta:</span> {fundamentals.beta ?? "N/A"}
            </li>
          </ul>
        ) : (
          <div className="muted">
            Load data to see fundamentals for this symbol.
          </div>
        )}
      </div>

      {/* Prediction */}
      <div className="card info-card">
        <div className="prediction-header">
          <h2>Prediction (XGBoost)</h2>
          <button
            className="btn secondary-btn"
            onClick={onPredictClick}
            disabled={predictionLoading}
          >
            {predictionLoading ? "Predicting..." : "Predict"}
          </button>
        </div>
        {prediction ? (
          prediction.error ? (
            <div className="error-text">{prediction.error}</div>
          ) : (
            <div className="prediction-body">
              <div className="prediction-row">
                <span>Direction:</span>{" "}
                <strong
                  className={
                    prediction.direction === "UP" ? "green" : "red"
                  }
                >
                  {prediction.direction}
                </strong>
              </div>
              <div className="prediction-row">
                <span>Suggestion:</span> {prediction.suggestion}
              </div>
              <div className="prediction-row">
                <span>Live Price:</span> ₹{prediction.live_price}
              </div>
              <div className="prediction-row">
                <span>Predicted Price:</span> ₹{prediction.predicted_price}
              </div>
              <div className="prediction-row">
                <span>Confidence:</span> {prediction.confidence}%
              </div>
            </div>
          )
        ) : (
          <div className="muted">
            Click <b>Predict</b> to get a direction.
          </div>
        )}
      </div>
    </section>
  );
}

export default Sidebar;
