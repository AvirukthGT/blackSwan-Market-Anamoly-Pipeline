{{ config(
    materialized='incremental',
    unique_key='news_id'
) }}

WITH source AS (
    SELECT * FROM {{ source('blackswan_raw', 'RAW_MARKET_NEWS') }}
),

renamed AS (
    SELECT
        -- 1. UNIQUE ID
        -- URLs are excellent unique keys for news (duplicates usually have same URL)
        src:link::STRING as news_id,

        -- 2. IDENTIFIERS
        src:symbol::STRING as symbol,

        -- 3. CONTENT
        src:title::STRING as title,
        src:summary::STRING as summary,
        src:link::STRING as url,

        -- 4. TIMESTAMPS
        -- A. Published Time (RSS Format)
        -- Snowflake's TRY_TO_TIMESTAMP is smart enough to parse "Sat, 17 Jan..." automatically
        TRY_TO_TIMESTAMP(src:published::STRING) as published_at,

        -- B. Producer Time (Apply the NUMBER(38,6) fix again!)
        TO_TIMESTAMP(src:ingestion_timestamp::NUMBER(38, 6)) as producer_time,

        -- C. Warehouse Time
        ingest_timestamp as warehouse_time

    FROM source
)

SELECT * FROM renamed

{% if is_incremental() %}
  -- Only process new rows since the last run
  WHERE warehouse_time > (SELECT max(warehouse_time) FROM {{ this }})
{% endif %}
