import json
import logging
import os
import time

import yfinance as yf
from confluent_kafka import Producer

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC_NAME = "stock_prices"

# ADDED BTC-USD so you see live data on weekends!
SYMBOLS = [
    "AAPL",
    "TSLA",
    "MSFT",
    "GOOGL",
    "AMZN",
    "BTC-USD",
    "ETH-USD",
    "SOL-USD",
    "XRP-USD",
    "DOGE-USD",
]


def get_stock_price(symbol):
    """Fetches real-time price data using yfinance."""
    try:
        ticker = yf.Ticker(symbol)

        # Crypto needs a different query sometimes, but '1d' '1m' usually works
        data = ticker.history(period="1d", interval="1m")

        if data.empty:
            logger.warning(f"No price data found for {symbol}")
            return None

        # Get the most recent row
        latest = data.iloc[-1]

        return {
            "symbol": symbol,
            "timestamp": str(latest.name),
            "open": float(latest["Open"]),
            "high": float(latest["High"]),
            "low": float(latest["Low"]),
            "close": float(latest["Close"]),
            "volume": int(latest["Volume"]),
        }
    except Exception as e:
        logger.error(f"Error fetching price for {symbol}: {e}")
        return None


def delivery_report(err, msg):
    if err is not None:
        logger.error(f"Delivery failed: {err}")


def main():
    producer = Producer(
        {
            "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
            "client.id": "price-producer-fast",
        }
    )

    logger.info(f"High-Speed Price Producer started. Tracking: {SYMBOLS}")

    while True:
        for symbol in SYMBOLS:
            stock_data = get_stock_price(symbol)

            if stock_data:
                stock_data["ingestion_timestamp"] = time.time()
                producer.produce(
                    TOPIC_NAME,
                    key=symbol,
                    value=json.dumps(stock_data),
                    callback=delivery_report,
                )
                logger.info(f"Sent {symbol}: ${stock_data['close']}")

            # Sleep 1 second between symbols to be polite
            time.sleep(1)

        producer.flush()

        # CHANGED: Sleep only 5 seconds instead of 60!
        logger.info("Cycle complete. Sleeping for 10 seconds...")
        time.sleep(10)


if __name__ == "__main__":
    main()
