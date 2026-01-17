{{ config(
    materialized='table'
) }}

WITH market_data AS (
    SELECT * FROM {{ ref('mart_technical_indicators') }}
    -- Rolling 24-hour window
    WHERE event_time >= DATEADD('hour', -24, CURRENT_TIMESTAMP())
),

aggregated AS (
    SELECT
        asset_type,
        symbol,

        -- 1. GET LATEST VALUES
        -- We use Snowflake's efficient ARRAY_AGG to grab the "Last" value without a join
        GET(ARRAY_AGG(close_price) WITHIN GROUP (ORDER BY event_time DESC), 0)::FLOAT as current_price,
        GET(ARRAY_AGG(market_sentiment) WITHIN GROUP (ORDER BY event_time DESC), 0)::FLOAT as current_sentiment,

        -- 2. CALCULATE AGGREGATES
        AVG(market_sentiment) as avg_sentiment_24h,
        STDDEV(close_price) as volatility_24h,

        -- "Tick Volume": How many times did the price update? (Proxy for activity)
        COUNT(*) as tick_volume

    FROM market_data
    GROUP BY 1, 2
)

SELECT
    *,
    -- 3. GENERATE RANKS (The "Leaderboard" Logic)

    -- Rank 1 = Most Positive Sentiment
    RANK() OVER (PARTITION BY asset_type ORDER BY avg_sentiment_24h DESC) as rank_bullish,

    -- Rank 1 = Most Negative Sentiment (The "Hated" list)
    RANK() OVER (PARTITION BY asset_type ORDER BY avg_sentiment_24h ASC) as rank_bearish,

    -- Rank 1 = Most Volatile (The "Risky" list)
    RANK() OVER (PARTITION BY asset_type ORDER BY volatility_24h DESC) as rank_volatility

FROM aggregated
ORDER BY asset_type, rank_bullish
