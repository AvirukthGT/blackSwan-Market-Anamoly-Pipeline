{{ config(
    materialized='table',
    cluster_by=['asset_type', 'symbol', 'event_time']
) }}

WITH prices AS (
    SELECT * FROM {{ ref('stg_stock_prices') }}
),

sentiment AS (
    SELECT * FROM {{ ref('stg_social_sentiment') }}
),

-- 1. Segregate & Aggregate Sentiment per Symbol/Hour
-- FIX: Changed 'event_time' to 'producer_time' because that is what we called it in stg_social_sentiment
sentiment_daily AS (
    SELECT
        DATE_TRUNC('hour', producer_time) as hour_bucket,
        CASE
            WHEN subreddit IN ('bitcoin', 'crypto', 'ethereum') THEN 'CRYPTO'
            ELSE 'STOCK'
        END as sentiment_type,
        AVG(sentiment) as avg_sentiment_score,
        SUM(upvotes) as total_attention
    FROM sentiment
    GROUP BY 1, 2
),

base_indicators AS (
    SELECT
        symbol,
        event_time,
        close_price,
        volume,

        -- 2. SEGREGATION LOGIC
        -- Simple rule: If it pairs with USD/USDT or is known crypto, tag it.
        CASE
            WHEN symbol LIKE '%-USD' OR symbol IN ('BTC', 'ETH', 'DOGE', 'SOL') THEN 'CRYPTO'
            ELSE 'STOCK'
        END as asset_type,

        -- 3. ALGO INDICATORS (Window Functions)
        -- A. Simple Moving Averages (Trend)
        AVG(close_price) OVER (
            PARTITION BY symbol
            ORDER BY event_time
            ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
        ) as sma_5_tick,

        -- B. Volatility (Bollinger Band Basis)
        STDDEV(close_price) OVER (
            PARTITION BY symbol
            ORDER BY event_time
            ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
        ) as volatility_20_tick,

        -- C. Previous Price (for calculating velocity)
        LAG(close_price, 1) OVER (PARTITION BY symbol ORDER BY event_time) as prev_price

    FROM prices
)

SELECT
    b.asset_type,
    b.symbol,
    b.event_time,
    b.close_price,
    b.sma_5_tick,
    b.volatility_20_tick,

    -- Calculate % Change (Momentum)
    (b.close_price - b.prev_price) / NULLIF(b.prev_price, 0) as price_change_pct,

    -- Join Sentiment (Using loose join on time and type for now)
    COALESCE(s.avg_sentiment_score, 0) as market_sentiment,

    -- 4. THE BLACK SWAN SIGNAL
    -- Logic: If Price is UP but Sentiment is Negative, that's a divergence.
    CASE
        WHEN b.close_price > b.sma_5_tick AND COALESCE(s.avg_sentiment_score, 0) < -0.2 THEN 'BEARISH_DIVERGENCE'
        WHEN b.close_price < b.sma_5_tick AND COALESCE(s.avg_sentiment_score, 0) > 0.2 THEN 'BULLISH_DIVERGENCE'
        ELSE 'NEUTRAL'
    END as black_swan_signal

FROM base_indicators b
LEFT JOIN sentiment_daily s
    ON DATE_TRUNC('hour', b.event_time) = s.hour_bucket
    AND b.asset_type = s.sentiment_type
