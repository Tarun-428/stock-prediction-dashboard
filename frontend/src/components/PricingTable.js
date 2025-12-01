// src/components/PricingTable.js
import React from "react";

function PricingTable({ pricing }) {
  if (!pricing || pricing.length === 0) return null;

  return (
    <div className="card table-card">
      <h2>Pricing Data</h2>
      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Open</th>
              <th>High</th>
              <th>Low</th>
              <th>Close</th>
              <th>Adj Close</th>
              <th>Volume</th>
              <th>% Change</th>
            </tr>
          </thead>
          <tbody>
            {pricing.slice(0, 50).map((row, idx) => (
              <tr key={idx}>
                <td>{row.Date}</td>
                <td>{row.Open}</td>
                <td>{row.High}</td>
                <td>{row.Low}</td>
                <td>{row.Close}</td>
                <td>{row["Adj Close"]}</td>
                <td>{row.Volume}</td>
                <td>{row["% Change"].toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default PricingTable;
