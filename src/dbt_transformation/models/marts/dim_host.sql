{{ config(materialized='table') }}

with source as (
    select
        host_id,
        host_name
    from {{ ref('stg_listings') }}
    where host_id is not null
),

deduplicated as (
    select distinct * from source
)

select * from deduplicated
