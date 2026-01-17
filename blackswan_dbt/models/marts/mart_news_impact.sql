{{ config(
    materialized='table'
) }}

WITH news AS (
    SELECT * FROM {{ ref('stg_market_news') }}
),

prices AS (
    SELECT symbol, event_time, close_price
    FROM {{ ref('mart_technical_indicators') }}
),

-- 1. Find the Last Known Price BEFORE the news (Start Price)
start_prices AS (
    SELECT
        n.news_id,
        p.close_price as start_price,
        p.event_time as start_time
    FROM news n
    LEFT JOIN prices p
        ON n.symbol = p.symbol
        AND p.event_time <= n.published_at -- Look backwards
    -- "Qualify" keeps only the very last row (closest to news time)
    QUALIFY ROW_NUMBER() OVER (PARTITION BY n.news_id ORDER BY p.event_time DESC) = 1
),

-- 2. Find the First Price at least 30 mins AFTER the news (End Price)
end_prices AS (
    SELECT
        n.news_id,
        p.close_price as end_price,
        p.event_time as end_time
    FROM news n
    LEFT JOIN prices p
        ON n.symbol = p.symbol
        AND p.event_time >= DATEADD('minute', 30, n.published_at) -- Look forwards
    -- "Qualify" keeps only the very first row found
    QUALIFY ROW_NUMBER() OVER (PARTITION BY n.news_id ORDER BY p.event_time ASC) = 1
)

SELECT
    n.news_id,
    n.title,
    n.url,
    n.published_at,
    n.symbol,

    -- Bring in the fuzzy-matched prices
    s.start_price,
    e.end_price,

    -- Debug columns: See how far apart the data actually was
    s.start_time,
    e.end_time,

    -- Calculate Impact
    CASE
        WHEN s.start_price IS NOT NULL AND e.end_price IS NOT NULL THEN
            (e.end_price - s.start_price) / NULLIF(s.start_price, 0)
        ELSE 0
    END as impact_pct,

    CASE
        WHEN s.start_price IS NULL THEN 'NO_PRICE_DATA'
        WHEN (e.end_price - s.start_price) / NULLIF(s.start_price, 0) > 0.01 THEN 'POSITIVE_SURGE'
        WHEN (e.end_price - s.start_price) / NULLIF(s.start_price, 0) < -0.01 THEN 'NEGATIVE_CRASH'
        ELSE 'NEUTRAL'
    END as impact_type

FROM news n
LEFT JOIN start_prices s ON n.news_id = s.news_id
LEFT JOIN end_prices e ON n.news_id = e.news_id
ORDER BY n.published_at DESC
