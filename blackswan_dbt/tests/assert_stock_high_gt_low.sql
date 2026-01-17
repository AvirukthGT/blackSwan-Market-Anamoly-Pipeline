-- tests/assert_stock_high_gt_low.sql

SELECT
    event_id,
    symbol,
    event_time,
    high_price,
    low_price
FROM {{ ref('stg_stock_prices') }}
WHERE low_price > high_price