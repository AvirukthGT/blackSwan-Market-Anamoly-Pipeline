import json
import logging
import os
import random
import time
import uuid

from confluent_kafka import Producer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC_NAME = "social_sentiment"

# --- DATA DICTIONARIES ---

TICKERS = [
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
SUBREDDITS = [
    "wallstreetbets",
    "stocks",
    "investing",
    "cryptocurrency",
    "options",
    "bitcoin",
    "ethereum",
    "solana",
    "dogecoin",
]

# Slang unique to Reddit investing subcultures
SLANG = [
    "diamond hands",
    "paper hands",
    "to the moon",
    "HODL",
    "yolo",
    "smooth brain",
    "ape strong",
    "tendies",
    "loss porn",
    "bag holder",
]

# BULLISH (Positive) Components
BULL_TEMPLATES = [
    "{ticker} is literally free money right now {emoji}",
    "Just bought more {ticker}, who is with me? {emoji}",
    "If {ticker} hits ${price}, I'm retiring early.",
    "{ticker} earnings are going to crush estimates!",
    "Stop selling {ticker} you cowards! {slang} {emoji}",
    "{ticker} chart looks insanely bullish.",
    "Imagine not owning {ticker} in 2026 {emoji}",
    "{ticker} is the next big thing!",
    "{ticker} is going to the moon!",
    "OMG {ticker} is on crack rn",
    "Oh lord I love this, {ticker} is going to make the capitalists rich",
]

# BEARISH (Negative) Components
BEAR_TEMPLATES = [
    "{ticker} is a rug pull, get out while you can {emoji}",
    "Just sold all my {ticker}, market is tanking.",
    "{ticker} is overvalued trash.",
    "My puts on {ticker} are printing money today {emoji}",
    "{ticker} is going to zero, mark my words.",
    "Why is {ticker} dropping so hard? {emoji}",
    "I lost my life savings on {ticker} calls... {slang}",
    "I can't believe I bought {ticker}",
]

# CHAOS / NEUTRAL Components
CHAOS_TEMPLATES = [
    "What do you guys think about {ticker}?",
    "Does anyone understand why {ticker} is moving like this?",
    "{ticker} volatility is insane right now.",
    "Should I yolo my rent money into {ticker}?",
    "{ticker} is the only thing keeping my portfolio alive.",
    "I'm not sure if I should buy {ticker} or not",
    "I'm not sure if I should sell {ticker} or not",
]

EMOJIS = ["🚀", "💎", "🙌", "🔥", "💀", "📉", "📈", "🤡", "🦍", "🌙"]


def generate_varied_post():
    """Generates a highly varied fake Reddit post."""

    # 1. Pick a Sentiment (40% Bull, 40% Bear, 20% Chaos)
    sentiment_roll = random.random()
    if sentiment_roll < 0.4:
        template = random.choice(BULL_TEMPLATES)
        sentiment_score = random.uniform(0.5, 1.0)  # Positive score
    elif sentiment_roll < 0.8:
        template = random.choice(BEAR_TEMPLATES)
        sentiment_score = random.uniform(-1.0, -0.5)  # Negative score
    else:
        template = random.choice(CHAOS_TEMPLATES)
        sentiment_score = random.uniform(-0.2, 0.2)  # Neutral score

    # 2. Fill in the blanks
    ticker = random.choice(TICKERS)
    text = template.format(
        ticker=ticker,
        emoji=random.choice(EMOJIS),
        slang=random.choice(SLANG),
        price=random.randint(100, 3000),
    )

    # 3. Add Human "Noise" (Typos, CAPS, repeating chars)
    if random.random() < 0.3:
        text = text.upper()  # ANGRY TRADER
    if random.random() < 0.2:
        text = text.replace(".", "!!!")  # Excited trader

    return {
        "platform": "reddit",
        "id": str(uuid.uuid4()),
        "title": text,
        "author": f"user_{random.randint(1000, 9999)}",
        "subreddit": random.choice(SUBREDDITS),
        "url": f"https://reddit.com/r/wsb/{str(uuid.uuid4())[:5]}",
        "score": random.randint(-5, 1500),
        "sentiment_score": round(sentiment_score, 2),  # Helpful for AI later!
        "ingestion_timestamp": time.time(),
    }


def delivery_report(err, msg):
    if err is not None:
        logger.error(f"Delivery failed: {err}")


def main():
    producer = Producer(
        {
            "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
            "client.id": "reddit-producer-advanced",
        }
    )

    logger.info("Advanced Reddit Simulator Started (High Variance Mode)")

    while True:
        post = generate_varied_post()

        producer.produce(
            TOPIC_NAME,
            key=post["subreddit"],
            value=json.dumps(post),
            callback=delivery_report,
        )

        # Log less frequently to keep terminal clean
        logger.info(f"[{post['subreddit']}] {post['title']}")

        producer.poll(0)

        # Random sleep to mimic organic traffic (tweets/posts come in bursts)
        time.sleep(random.uniform(1.5, 5.0))


if __name__ == "__main__":
    main()
