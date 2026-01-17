from app.database import engine
from sqlalchemy import text

print("Attempting to connect...", flush=True)
try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT CURRENT_VERSION()"))
        print(f"Success! Snowflake Version: {result.fetchone()[0]}")
except Exception as e:
    print(f"CONNECTION FAILED: {e}")
    import traceback
    traceback.print_exc()
