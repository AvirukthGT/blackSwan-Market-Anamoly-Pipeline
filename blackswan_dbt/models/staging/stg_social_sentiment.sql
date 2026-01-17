{{ config(
    materialized='incremental',
    unique_key='post_id'
) }}

WITH source AS (
    SELECT * FROM {{ source('blackswan_raw', 'RAW_SOCIAL_SENTIMENT') }}
),

renamed AS (
    SELECT
        -- 1. UNIQUE ID
        src:id::STRING as post_id,

        -- 2. METADATA
        src:platform::STRING as platform,
        src:subreddit::STRING as subreddit,
        src:author::STRING as author,
        src:title::STRING as content, -- Renaming 'title' to 'content' fits better for tweets/comments
        src:url::STRING as url,

        -- 3. METRICS
        src:score::INTEGER as upvotes,
        src:sentiment_score::FLOAT as sentiment,

        -- 4. TIMESTAMPS
        -- Producer Time (The "38,6" fix)
        TO_TIMESTAMP(src:ingestion_timestamp::NUMBER(38, 6)) as producer_time,

        -- Warehouse Time
        ingest_timestamp as warehouse_time

    FROM source
)

SELECT * FROM renamed

{% if is_incremental() %}
  WHERE warehouse_time > (SELECT max(warehouse_time) FROM {{ this }})
{% endif %}
