# Use an official Python runtime parent image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# 1. Install system dependencies
# - gcc & g++: Required for confluent-kafka and snowflake-connector
# - python3-dev: Required for C extensions
# - libpq-dev: Often needed for database connectors
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Upgrade pip (Important for Python 3.12 compatibility)
RUN pip install --no-cache-dir --upgrade pip

# 3. Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of the application
COPY . .

CMD ["python"]
