{{ config(materialized='table') }}

with source as (
    select
        id as listing_id,
        name,
        latitude,
        longitude
    from {{ ref('stg_listings') }}
    where id is not null
),

deduplicated as (
    select distinct * from source
)

select * from deduplicated
