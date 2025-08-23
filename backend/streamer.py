import asyncio, websockets, json, os, threading
from flask import Flask, request, jsonify
from flask_cors import CORS

API_KEY = os.environ.get("TWELVEDATA_API_KEY")  # set this in docker-compose
TD_WS_URL = f"wss://ws.twelvedata.com/v1/quotes/price?apikey={API_KEY}"

app = Flask(__name__)
CORS(app)

latest_prices = {}

def start_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

async def listen_tds():
    symbols = ["AAPL", "GOOGL"]  # change this list as needed
    async with websockets.connect(TD_WS_URL) as ws:
        await ws.send(json.dumps({ "action": "subscribe", "params": { "symbols": ",".join(symbols) } }))
        async for msg in ws:
            data = json.loads(msg)
            if data.get("event") == "price":
                s = data["symbol"]
                latest_prices[s] = { **data, "timestamp": data["datetime"] }

loop = asyncio.new_event_loop()
threading.Thread(target=start_loop, args=(loop,), daemon=True).start()
asyncio.run_coroutine_threadsafe(listen_tds(), loop)

@app.route("/stream-subscribe", methods=["POST"])
def stream_subscribe():
    return jsonify({"message": "Subscribed"}), 200

@app.route("/stream-price", methods=["GET"])
def stream_price():
    symbol = request.args.get("symbol", "").upper()
    if symbol in latest_prices:
        return jsonify(latest_prices[symbol])
    return jsonify({"error": "No data yet for symbol"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
