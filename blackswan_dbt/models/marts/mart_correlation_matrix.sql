{{ config(
    materialized='table'
) }}

WITH relevant_assets AS (
    -- 1. Filter to only the Top 50 most active assets
    SELECT symbol
    FROM {{ ref('mart_trending_assets') }}
    -- FIX: Use 'tick_volume' instead of 'total_volume'
    ORDER BY tick_volume DESC
    LIMIT 50
),

returns_data AS (
    -- 2. Get the hourly % returns for these assets over the last 30 days
    SELECT
        symbol,
        DATE_TRUNC('hour', event_time) as hour_bucket,
        AVG(price_change_pct) as hourly_return
    FROM {{ ref('mart_technical_indicators') }}
    WHERE symbol IN (SELECT symbol FROM relevant_assets)
      AND event_time >= DATEADD('day', -30, CURRENT_TIMESTAMP())
    GROUP BY 1, 2
),

pairs AS (
    -- 3. Self-Join to create every possible pair (A vs B)
    SELECT
        r1.symbol as symbol_a,
        r2.symbol as symbol_b,
        r1.hourly_return as return_a,
        r2.hourly_return as return_b
    FROM returns_data r1
    INNER JOIN returns_data r2
        ON r1.hour_bucket = r2.hour_bucket
        AND r1.symbol <> r2.symbol
)

SELECT
    symbol_a,
    symbol_b,

    -- 4. Calculate Correlation
    CORR(return_a, return_b) as correlation_score,

    -- 5. Interpretation
    CASE
        WHEN CORR(return_a, return_b) > 0.7 THEN 'Strong Lockstep'
        WHEN CORR(return_a, return_b) > 0.3 THEN 'Moderate Lockstep'
        WHEN CORR(return_a, return_b) < -0.5 THEN 'Inverse Mover'
        ELSE 'Uncorrelated'
    END as relationship_type

FROM pairs
GROUP BY 1, 2
HAVING ABS(correlation_score) > 0.1
ORDER BY symbol_a, correlation_score DESC
