// src/components/PriceChart.js
import React, { useMemo } from "react";
import Chart from "react-apexcharts";

// keep at most N points to avoid freezing the page
function downsamplePoints(points, maxPoints = 400) {
  if (!points || points.length <= maxPoints) return points || [];
  const step = Math.ceil(points.length / maxPoints);
  return points.filter((_, idx) => idx % step === 0);
}

function PriceChart({ symbol, timeframe, chartData }) {
  const processedPoints = useMemo(() => {
    if (!chartData) return [];

    const raw = chartData.dates.map((d, i) => ({
      date: new Date(d),
      open: Number(chartData.open[i]),
      high: Number(chartData.high[i]),
      low: Number(chartData.low[i]),
      close: Number(chartData.close[i]),
      volume: Number(chartData.volume[i]),
    }));

    return downsamplePoints(raw, 400);
  }, [chartData]);

  const candlestickSeries = useMemo(() => {
    if (!processedPoints.length) return [];
    return [
      {
        name: "Price",
        data: processedPoints.map((p, idx) => ({
          x: idx,
          y: [p.open, p.high, p.low, p.close],
        })),
      },
    ];
  }, [processedPoints]);

  const volumeSeries = useMemo(() => {
    if (!processedPoints.length) return [];
    return [
      {
        name: "Volume",
        data: processedPoints.map((p, idx) => ({
          x: idx,
          y: p.volume,
        })),
      },
    ];
  }, [processedPoints]);

  const chartOptions = useMemo(
    () => ({
      chart: {
        type: "candlestick",
        toolbar: {
          show: true,
          tools: {
            download: true,
            selection: true,
            zoom: true,
            zoomin: true,
            zoomout: true,
            pan: true,
            reset: true,
          },
          autoSelected: "zoom",
        },
      },
      xaxis: {
        type: "category",
        labels: {
          formatter(value) {
            const idx = parseInt(value, 10);
            if (Number.isNaN(idx) || !processedPoints[idx]) return "";
            const d = processedPoints[idx].date;
            return d.toLocaleString("en-IN", {
              day: "2-digit",
              month: "short",
              hour: "2-digit",
              minute: "2-digit",
            });
          },
        },
      },
      yaxis: {
        tooltip: { enabled: true },
      },
      tooltip: {
        shared: true,
        x: {
          formatter(_, opts) {
            const idx = opts.dataPointIndex;
            if (!processedPoints[idx]) return "";
            const d = processedPoints[idx].date;
            return d.toLocaleString("en-IN", {
              year: "numeric",
              month: "short",
              day: "2-digit",
              hour: "2-digit",
              minute: "2-digit",
            });
          },
        },
      },
    }),
    [processedPoints]
  );

  const volumeOptions = useMemo(
    () => ({
      chart: {
        type: "bar",
        toolbar: { show: false },
      },
      xaxis: {
        type: "category",
        labels: { show: false },
      },
    }),
    []
  );

  if (!chartData || !processedPoints.length) return null;

  return (
    <div className="card chart-card">
      <h2>
        {symbol} Price Chart{" "}
        <span className="timeframe-label">({timeframe.label})</span>
      </h2>
      <Chart
        options={chartOptions}
        series={candlestickSeries}
        type="candlestick"
        height={400}
      />
      <div className="volume-chart">
        <Chart
          options={volumeOptions}
          series={volumeSeries}
          type="bar"
          height={120}
        />
      </div>
    </div>
  );
}

export default PriceChart;
