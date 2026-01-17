from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import get_db
from sqlalchemy import text

app = FastAPI(title="Black Swan Sentiment Engine API")

# Enable CORS for frontend
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/signals")
def get_signals(asset_class: str = "STOCK", db: Session = Depends(get_db)):
    # Simple logic: Crypto symbols end with '-USD' or are in a known list
    # We filter using LIKE logic for now since mart_algo_signals doesn't have asset_type column
    
    if asset_class.upper() == "CRYPTO":
        condition = "SYMBOL LIKE '%-USD%'"
    else:
        condition = "SYMBOL NOT LIKE '%-USD%'"

    query = text(f"""
        SELECT * FROM MARTS.MART_ALGO_SIGNALS 
        WHERE {condition}
        ORDER BY EVENT_TIME DESC 
        LIMIT 100
    """)
    
    result = db.execute(query)
    
    # Convert rows to list of dictionaries for JSON response
    return [dict(row._mapping) for row in result]

@app.get("/api/news")
def get_news(db: Session = Depends(get_db)):
    query = text("""
        SELECT * FROM MARTS.MART_NEWS_IMPACT 
        ORDER BY PUBLISHED_AT DESC 
        LIMIT 50
    """)
    result = db.execute(query)
    return [dict(row._mapping) for row in result]



@app.get("/api/performance")
def get_performance(db: Session = Depends(get_db)):
    query = text("""
        SELECT * FROM MARTS.MART_SECTOR_PERFORMANCE 
        ORDER BY avg_sector_return DESC
    """)
    result = db.execute(query)
    # Snowflake returns uppercase keys, so we lower them effectively in the FE or here.
    # Let's verify what comes out, likely uppercase.
    return [dict(row._mapping) for row in result]

@app.get("/api/correlations")
def get_correlations(symbol: str = None, db: Session = Depends(get_db)):
    # If no symbol provided, just get top strong correlations
    if symbol:
        query = text(f"""
            SELECT * FROM MARTS.MART_CORRELATION_MATRIX 
            WHERE symbol_a = '{symbol}' OR symbol_b = '{symbol}'
            ORDER BY ABS(correlation_score) DESC
            LIMIT 10
        """)
    else:
        query = text("""
            SELECT * FROM MARTS.MART_CORRELATION_MATRIX 
            ORDER BY ABS(correlation_score) DESC
            LIMIT 20
        """)
    result = db.execute(query)
    return [dict(row._mapping) for row in result]

@app.get("/api/history/{symbol}")
def get_history(symbol: str, db: Session = Depends(get_db)):
    # Fetch last 200 data points for detailing
    query = text(f"""
        SELECT event_time, close_price 
        FROM MARTS.MART_TECHNICAL_INDICATORS
        WHERE symbol = '{symbol}'
        ORDER BY event_time ASC
        LIMIT 200
    """)
    result = db.execute(query)
    return [dict(row._mapping) for row in result]

@app.get("/api/trending")
def get_trending(db: Session = Depends(get_db)):
    query = text("""
        SELECT * FROM MARTS.MART_TRENDING_ASSETS
        ORDER BY tick_volume DESC
        LIMIT 50
    """)
    result = db.execute(query)
    return [dict(row._mapping) for row in result]

@app.get("/api/reddit")
def get_reddit(db: Session = Depends(get_db)):
    query = text("""
        SELECT * FROM STAGING.STG_SOCIAL_SENTIMENT 
        WHERE platform = 'reddit'
        ORDER BY producer_time DESC 
        LIMIT 50
    """)
    result = db.execute(query)
    return [dict(row._mapping) for row in result]