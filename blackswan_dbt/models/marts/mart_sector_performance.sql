{{ config(
    materialized='table'
) }}

WITH base_data AS (
    SELECT
        asset_type,
        symbol,
        event_time,
        price_change_pct,
        market_sentiment,
        black_swan_signal
    FROM {{ ref('mart_technical_indicators') }}
    -- Look at the last 60 minutes of data for a "Live" heatmap
    WHERE event_time >= DATEADD('hour', -1, CURRENT_TIMESTAMP())
),

sector_stats AS (
    SELECT
        asset_type,

        -- 1. Sector Performance (Weighted Average could be better, but simple AVG works for now)
        AVG(price_change_pct) as avg_sector_return,
        AVG(market_sentiment) as avg_sector_sentiment,

        -- 2. Market Breadth (The "Advance/Decline" Line)
        COUNT_IF(price_change_pct > 0) as count_gainers,
        COUNT_IF(price_change_pct < 0) as count_losers,
        COUNT(*) as total_active_assets,

        -- 3. Risk Signals
        COUNT_IF(black_swan_signal = 'BEARISH_DIVERGENCE') as sector_bearish_signals

    FROM base_data
    GROUP BY 1
)

SELECT
    *,
    -- Calculate the "Heat" (Breadth Ratio)
    -- If > 0.5, the majority of the sector is Green. If < 0.5, Red.
    count_gainers / NULLIF(total_active_assets, 0) as breadth_ratio,

    -- Status Message for UI
    CASE
        WHEN breadth_ratio < 0.2 THEN 'SECTOR_CRASH'      -- >80% of assets are down
        WHEN breadth_ratio < 0.4 THEN 'BEARISH_LEAN'
        WHEN breadth_ratio > 0.8 THEN 'SECTOR_RALLY'      -- >80% of assets are up
        ELSE 'MIXED_MARKET'
    END as sector_status

FROM sector_stats
ORDER BY avg_sector_return DESC
