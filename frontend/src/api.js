// src/api.js
import axios from "axios";

const API_BASE_URL = "http://localhost:5000"; // change if backend is elsewhere

export async function getStockData(symbol, start, end) {
  const res = await axios.get(`${API_BASE_URL}/stock-data`, {
    params: { symbol, start, end },
  });
  return res.data;
}

export async function getPrediction(symbol) {
  const res = await axios.get(`${API_BASE_URL}/predict`, {
    params: { symbol },
  });
  return res.data;
}

export async function getLivePrice(symbol) {
  const res = await axios.get(`${API_BASE_URL}/live-price`, {
    params: { symbol },
  });
  return res.data;
}
