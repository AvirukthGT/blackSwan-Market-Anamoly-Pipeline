import json
import logging
import os
import time
from datetime import datetime

import boto3
from confluent_kafka import Consumer
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration ---
KAFKA_BOOTSTRAP_SERVERS = os.getenv("BOOTSTRAP_SERVERS", "localhost:9092")
AWS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
REGION = os.getenv("AWS_REGION", "us-east-1")

TOPICS = ["stock_prices", "market_news", "social_sentiment"]

# Buffer Config
BATCH_SIZE = 100  # Flush after 100 messages
FLUSH_INTERVAL = 60  # Flush after 60 seconds


def get_s3_client():
    try:
        return boto3.client(
            "s3",
            aws_access_key_id=AWS_KEY,
            aws_secret_access_key=AWS_SECRET,
            region_name=REGION,
        )
    except Exception as e:
        logger.error(f"Failed to create S3 client: {e}")
        return None


def upload_to_s3(s3_client, data, topic):
    if not data:
        return

    timestamp = int(time.time())
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{topic}/{date_str}/{timestamp}.json"

    try:
        body = json.dumps(data)
        s3_client.put_object(
            Bucket=BUCKET_NAME, Key=filename, Body=body, ContentType="application/json"
        )
        logger.info(f"Uploaded {len(data)} items to s3://{BUCKET_NAME}/{filename}")
    except Exception as e:
        logger.error(f"Failed to upload to S3: {e}")


def main():
    consumer = Consumer(
        {
            "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
            "group.id": "s3-uploader-group",
            "auto.offset.reset": "earliest",
        }
    )

    consumer.subscribe(TOPICS)
    s3_client = get_s3_client()

    logger.info(f"S3 Consumer started. Listening to: {TOPICS}")

    # 1. Separate buffers for each topic
    buffer = {topic: [] for topic in TOPICS}

    # 2. FIX: Separate timers for each topic
    last_flush_time = {topic: time.time() for topic in TOPICS}

    try:
        while True:
            # Poll for messages (non-blocking wait of 1s)
            msg = consumer.poll(1.0)

            if msg is not None:
                if not msg.error():
                    topic = msg.topic()
                    try:
                        payload = json.loads(msg.value().decode("utf-8"))
                        buffer[topic].append(payload)
                    except json.JSONDecodeError:
                        logger.error(f"JSON Error in {topic}")
                else:
                    logger.error(f"Consumer error: {msg.error()}")

            # Check Flush Conditions for EVERY topic independently
            current_time = time.time()

            for topic in TOPICS:
                # Calculate time since THIS TOPIC last flushed
                time_diff = current_time - last_flush_time[topic]

                # Check limits
                is_full = len(buffer[topic]) >= BATCH_SIZE
                is_old = time_diff > FLUSH_INTERVAL and len(buffer[topic]) > 0

                if is_full or is_old:
                    # ✅ FIXED
                    logger.info(
                        f"Flushing {topic} (Items: {len(buffer[topic])}, Age: {int(time_diff)}s)..."
                    )
                    upload_to_s3(s3_client, buffer[topic], topic)

                    # Reset only THIS topic's buffer and timer
                    buffer[topic] = []
                    last_flush_time[topic] = current_time

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()


if __name__ == "__main__":
    main()
