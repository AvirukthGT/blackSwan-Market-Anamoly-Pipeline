{{ config(materialized='table') }}

WITH base AS (
    SELECT
        symbol,
        event_time,
        close_price,
        -- Lagged price for calculations
        LAG(close_price, 1) OVER (PARTITION BY symbol ORDER BY event_time) as prev_price
    FROM {{ ref('stg_stock_prices') }}
),

price_changes AS (
    SELECT
        *,
        close_price - prev_price as change,
        CASE WHEN (close_price - prev_price) > 0 THEN (close_price - prev_price) ELSE 0 END as gain,
        CASE WHEN (close_price - prev_price) < 0 THEN ABS(close_price - prev_price) ELSE 0 END as loss
    FROM base
),

-- CALCULATE MOVING AVERAGES & BOLLINGER BANDS
indicators AS (
    SELECT
        symbol,
        event_time,
        close_price,

        -- 1. Simple Moving Averages (Trend)
        AVG(close_price) OVER (PARTITION BY symbol ORDER BY event_time ROWS BETWEEN 49 PRECEDING AND CURRENT ROW) as sma_50,
        AVG(close_price) OVER (PARTITION BY symbol ORDER BY event_time ROWS BETWEEN 199 PRECEDING AND CURRENT ROW) as sma_200,

        -- 2. Bollinger Bands (Volatility)
        AVG(close_price) OVER (PARTITION BY symbol ORDER BY event_time ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) as bb_middle,
        STDDEV(close_price) OVER (PARTITION BY symbol ORDER BY event_time ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) as bb_stddev,

        -- 3. MACD Components (Approximation using SMA for simplicity, or specific EMA macro if available)
        AVG(close_price) OVER (PARTITION BY symbol ORDER BY event_time ROWS BETWEEN 11 PRECEDING AND CURRENT ROW) as ema_12,
        AVG(close_price) OVER (PARTITION BY symbol ORDER BY event_time ROWS BETWEEN 25 PRECEDING AND CURRENT ROW) as ema_26,

        -- 4. RSI Components (Rolling Avg Gain/Loss)
        AVG(gain) OVER (PARTITION BY symbol ORDER BY event_time ROWS BETWEEN 13 PRECEDING AND CURRENT ROW) as avg_gain_14,
        AVG(loss) OVER (PARTITION BY symbol ORDER BY event_time ROWS BETWEEN 13 PRECEDING AND CURRENT ROW) as avg_loss_14

    FROM price_changes
)

SELECT
    *,
    -- Final Bollinger Band Calculations
    bb_middle + (2 * bb_stddev) as bb_upper,
    bb_middle - (2 * bb_stddev) as bb_lower,

    -- Final RSI Calculation (100 - (100 / (1 + RS)))
    100 - (100 / (1 + DIV0(avg_gain_14, avg_loss_14))) as rsi_14,

    -- Final MACD Line
    ema_12 - ema_26 as macd_line

FROM indicators
