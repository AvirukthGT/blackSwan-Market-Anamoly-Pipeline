{{ config(
    materialized='incremental',
    unique_key='event_id'
) }}

WITH source AS (
    SELECT * FROM {{ source('blackswan_raw', 'RAW_STOCK_PRICES') }}
),

renamed AS (
    SELECT
        -- 1. UNIQUE ID
        src:symbol::STRING || '-' || src:timestamp::STRING as event_id,

        -- 2. IDENTIFIERS
        src:symbol::STRING as symbol,

        -- 3. OHLC DATA
        src:open::FLOAT as open_price,
        src:high::FLOAT as high_price,
        src:low::FLOAT as low_price,
        src:close::FLOAT as close_price,
        COALESCE(src:volume::INTEGER, 0) as volume,

        -- 4. TIMESTAMPS
        -- Market Time (String -> Timestamp)
        TO_TIMESTAMP(src:timestamp::STRING) as event_time,

        -- Producer Time (Fix: Cast to NUMBER(38,6) for precision epoch)
        TO_TIMESTAMP(src:ingestion_timestamp::NUMBER(38, 6)) as producer_time,

        -- Warehouse Time
        ingest_timestamp as warehouse_time

    FROM source
)

SELECT * FROM renamed

{% if is_incremental() %}
  WHERE warehouse_time > (SELECT max(warehouse_time) FROM {{ this }})
{% endif %}
