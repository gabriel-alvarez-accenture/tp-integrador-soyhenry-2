{{ config(materialized='table') }}

with source as (
    select
        room_type
    from {{ ref('stg_listings') }}
    where room_type is not null
),

deduplicated as (
    select distinct room_type from source
),

final as (
    select
        row_number() over (order by room_type) as room_type_id,
        room_type
    from deduplicated
)

select * from final
