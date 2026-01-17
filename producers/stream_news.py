import json
import logging
import os
import time

import feedparser
from confluent_kafka import Producer

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC_NAME = "market_news"

# ADDED BTC-USD so we get crypto news too!
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


def get_rss_news(symbol):
    """Fetches news from Yahoo Finance RSS feeds."""
    # Yahoo's public RSS endpoint works for Crypto tickers too (e.g. BTC-USD)
    rss_url = f"https://finance.yahoo.com/rss/headline?s={symbol}"

    try:
        feed = feedparser.parse(rss_url)
        return feed.entries
    except Exception as e:
        logger.error(f"Error fetching RSS for {symbol}: {e}")
        return []


def delivery_report(err, msg):
    if err is not None:
        logger.error(f"Delivery failed: {err}")


def main():
    producer = Producer(
        {"bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS, "client.id": "news-producer-rss"}
    )

    logger.info(f"📰 Yahoo RSS News Producer started. Tracking: {SYMBOLS}")

    sent_guids = set()

    while True:
        for symbol in SYMBOLS:
            news_items = get_rss_news(symbol)

            count = 0
            for item in news_items:
                guid = item.get("id", item.get("link"))

                if guid and guid not in sent_guids:
                    payload = {
                        "symbol": symbol,
                        "title": item.get("title"),
                        "link": item.get("link"),
                        "published": item.get("published"),
                        "summary": item.get("summary"),
                        "ingestion_timestamp": time.time(),
                    }

                    producer.produce(
                        TOPIC_NAME,
                        key=symbol,
                        value=json.dumps(payload),
                        callback=delivery_report,
                    )

                    sent_guids.add(guid)
                    count += 1

            if count > 0:
                logger.info(f"Sent {count} articles for {symbol}")

        producer.flush()

        if len(sent_guids) > 5000:
            sent_guids.clear()

        logger.info("Cycle complete. Sleeping for 120 seconds...")
        time.sleep(120)


if __name__ == "__main__":
    main()
