{{ config(
    materialized='table',
    cluster_by=['strategy_name', 'symbol', 'event_time']
) }}

WITH indicators AS (
    SELECT * FROM {{ ref('int_technical_indicators') }}
),

-- Add "Previous" values to detect CROSSOVERS (e.g., Today it's above, Yesterday it was below)
crossover_setup AS (
    SELECT
        *,
        LAG(macd_line, 1) OVER (PARTITION BY symbol ORDER BY event_time) as prev_macd,
        LAG(rsi_14, 1) OVER (PARTITION BY symbol ORDER BY event_time) as prev_rsi,
        LAG(close_price, 1) OVER (PARTITION BY symbol ORDER BY event_time) as prev_close
    FROM indicators
)

SELECT
    symbol,
    event_time,
    close_price,
    'Combined_Signals' as strategy_name,
    -- STRATEGY 1: GOLDEN CROSS (Long Term Trend)
    -- Signal: Buy when SMA50 goes above SMA200. Sell when it drops below.
    CASE
        WHEN sma_50 > sma_200 AND LAG(sma_50, 1) OVER (PARTITION BY symbol ORDER BY event_time) <= LAG(sma_200, 1) OVER (PARTITION BY symbol ORDER BY event_time) THEN 'BUY_ENTRY'
        WHEN sma_50 < sma_200 AND LAG(sma_50, 1) OVER (PARTITION BY symbol ORDER BY event_time) >= LAG(sma_200, 1) OVER (PARTITION BY symbol ORDER BY event_time) THEN 'SELL_EXIT'
        ELSE 'HOLD'
    END as signal_golden_cross,

    -- STRATEGY 2: RSI REVERSAL (Short Term Scalp)
    -- Signal: Buy if RSI dips below 30. Sell if RSI breaks above 70.
    CASE
        WHEN rsi_14 < 30 THEN 'BUY_OVERSOLD'
        WHEN rsi_14 > 70 THEN 'SELL_OVERBOUGHT'
        ELSE 'NEUTRAL'
    END as signal_rsi_mean_reversion,

    -- STRATEGY 3: BOLLINGER BREAKOUT
    -- Signal: Price falls below lower band (Buy dip). Price hits upper band (Sell rip).
    CASE
        WHEN close_price < bb_lower THEN 'BUY_DIP'
        WHEN close_price > bb_upper THEN 'SELL_RIP'
        ELSE 'NEUTRAL'
    END as signal_bollinger_bands

FROM crossover_setup
WHERE event_time >= DATEADD('month', -6, CURRENT_TIMESTAMP()) -- Keep last 6 months hot
ORDER BY event_time DESC
