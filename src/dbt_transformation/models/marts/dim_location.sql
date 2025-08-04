{{ config(materialized='table') }}

with source as (
    select
        neighbourhood_group,
        neighbourhood
    from {{ ref('stg_listings') }}
    where neighbourhood is not null
),

deduplicated as (
    select distinct
        neighbourhood_group,
        neighbourhood
    from source
),

final as (
    select
        row_number() over (order by neighbourhood_group, neighbourhood) as location_id,
        neighbourhood_group,
        neighbourhood
    from deduplicated
)

select * from final
