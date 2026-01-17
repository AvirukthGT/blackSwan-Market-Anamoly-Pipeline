import json
import logging
import os
import time

import requests
from confluent_kafka import Producer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC_NAME = "market_news"


def get_news_sentiment():
    """Fetches live news sentiment data from Alpha Vantage."""
    # I'm using the 'NEWS_SENTIMENT' endpoint
    url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=AAPL,MSFT,TSLA&apikey={API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()

        if "feed" in data:
            return data["feed"]
        else:
            logger.warning(f"No feed found. Response: {data}")
            return []
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        return []


def delivery_report(err, msg):
    """Callback: I'll call this for each message to check if it reached Kafka."""
    if err is not None:
        logger.error(f"Message delivery failed: {err}")
    else:
        logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")


def main():
    # 1. Connect to the Kafka Broker
    producer = Producer(
        {"bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS, "client.id": "news-producer"}
    )
    logger.info(f"Connected to Kafka at {KAFKA_BOOTSTRAP_SERVERS}")

    # 2. Start the Infinite Loop
    while True:
        logger.info("Fetching latest news...")
        news_items = get_news_sentiment()

        if news_items:
            # I'm limiting this to 5 items to save API credits
            for item in news_items[:5]:
                # I'm adding a timestamp so I know when I ingested it
                item["ingestion_timestamp"] = time.time()

                # Send JSON to Kafka
                producer.produce(
                    TOPIC_NAME,
                    key=item.get("title", "unknown"),
                    value=json.dumps(item),
                    callback=delivery_report,
                )

            # Flush ensures the messages are actually sent over the network
            producer.flush()
            logger.info(f"Sent {len(news_items[:5])} articles to Kafka.")

        # Sleep for 60 seconds (Alpha Vantage Free Tier limit)
        logger.info("Sleeping for 60 seconds...")
        time.sleep(60)


if __name__ == "__main__":
    main()
