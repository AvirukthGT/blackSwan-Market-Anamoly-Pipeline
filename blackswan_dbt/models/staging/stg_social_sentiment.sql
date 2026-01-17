{{ config(
    materialized='incremental',
    unique_key='post_id'
) }}

WITH source AS (
    SELECT * FROM {{ source('blackswan_raw', 'RAW_SOCIAL_SENTIMENT') }}
),

renamed AS (
    SELECT
        src:id::STRING as post_id,
        src:platform::STRING as platform,
        src:subreddit::STRING as subreddit,
        src:author::STRING as author,
        src:title::STRING as content,
        src:url::STRING as url,
        src:score::INTEGER as upvotes,
        src:sentiment_score::FLOAT as sentiment,
        TO_TIMESTAMP(src:ingestion_timestamp::NUMBER(38, 6)) as producer_time,
        ingest_timestamp as warehouse_time
    FROM source
    
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY post_id 
        ORDER BY ingest_timestamp DESC
    ) = 1
)

SELECT * FROM renamed

{% if is_incremental() %}
  WHERE warehouse_time > (SELECT max(warehouse_time) FROM {{ this }})
{% endif %}