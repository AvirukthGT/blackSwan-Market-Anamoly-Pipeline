{{ config(
    materialized='incremental',
    unique_key='news_id'
) }}

WITH source AS (
    SELECT * FROM {{ source('blackswan_raw', 'RAW_MARKET_NEWS') }}
),

renamed AS (
    SELECT
        src:link::STRING as news_id,
        src:symbol::STRING as symbol,
        src:title::STRING as title,
        src:summary::STRING as summary,
        src:link::STRING as url,
        TRY_TO_TIMESTAMP(src:published::STRING) as published_at,
        TO_TIMESTAMP(src:ingestion_timestamp::NUMBER(38, 6)) as producer_time,
        ingest_timestamp as warehouse_time
    FROM source
),

deduplicated AS (
    SELECT
        *,
        -- Rank duplicates: if two rows have the same news_id,
        -- the one with the later producer_time gets row_num = 1
        ROW_NUMBER() OVER (
            PARTITION BY news_id
            ORDER BY producer_time DESC
        ) as row_num
    FROM renamed
    {% if is_incremental() %}
      -- Only look at rows newer than what we already have
      WHERE warehouse_time > (SELECT max(warehouse_time) FROM {{ this }})
    {% endif %}
)

-- Final select: filter out the duplicates (where row_num > 1)
SELECT
    news_id,
    symbol,
    title,
    summary,
    url,
    published_at,
    producer_time,
    warehouse_time
FROM deduplicated
WHERE row_num = 1
