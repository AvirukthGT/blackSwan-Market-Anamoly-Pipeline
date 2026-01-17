import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL
from dotenv import load_dotenv

load_dotenv()

# Fetch env vars
user = os.getenv("SNOWFLAKE_USER")
password = os.getenv("SNOWFLAKE_PASSWORD")
account = os.getenv("SNOWFLAKE_ACCOUNT")
database = os.getenv("SNOWFLAKE_DATABASE")
schema = os.getenv("SNOWFLAKE_SCHEMA")
warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")
role = os.getenv("SNOWFLAKE_ROLE")

# Debug: Print loaded config (masked password)
print(f"Connecting to Snowflake: Account={account}, User={user}, DB={database}, Schema={schema}", flush=True)

# Construct URL minimal
url = URL.create(
    "snowflake",
    username=user,
    password=password,
    host=account,
    database=database,
)

# Create engine with connect_args
# This is often more reliable than URL query params for complex args
engine = create_engine(
    url,
    connect_args={
        "schema": schema,
        "warehouse": warehouse,
        "role": role,
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()