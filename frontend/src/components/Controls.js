// src/components/Controls.js
import React from "react";
import { TIMEFRAMES } from "../constants";

function Controls({
  symbol,
  startDate,
  endDate,
  timeframe,
  loading,
  onSymbolChange,
  onStartDateChange,
  onEndDateChange,
  onTimeframeChange,
  onLoadClick,
}) {
  return (
    <div className="card control-card">
      <div className="control-row">
        <div className="form-group">
          <label>Symbol</label>
          <input
            type="text"
            value={symbol}
            onChange={(e) => onSymbolChange(e.target.value.toUpperCase())}
            placeholder="e.g. NIFTY, RELIANCE"
          />
        </div>

        <div className="form-group">
          <label>Start Date</label>
          <input
            type="date"
            value={startDate}
            onChange={(e) => onStartDateChange(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label>End Date</label>
          <input
            type="date"
            value={endDate}
            onChange={(e) => onEndDateChange(e.target.value)}
          />
        </div>

        <button
          className="btn primary-btn"
          onClick={onLoadClick}
          disabled={loading}
        >
          {loading ? "Loading..." : "Load Data"}
        </button>
      </div>

      <div className="timeframe-row">
        <span>Timeframe: </span>
        {TIMEFRAMES.map((tf) => (
          <button
            key={tf.label}
            className={
              "btn timeframe-btn" +
              (timeframe.label === tf.label ? " active" : "")
            }
            onClick={() => onTimeframeChange(tf)}
          >
            {tf.label}
          </button>
        ))}
      </div>
    </div>
  );
}

export default Controls;
