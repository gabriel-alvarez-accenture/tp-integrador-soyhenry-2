{{ config(materialized='table') }}

with source as (
    select * from {{ ref('stg_listings') }}
),

joined as (
    select
        s.id as listing_id,
        s.host_id,
        loc.location_id,
        rt.room_type_id,
        s.price,
        s.minimum_nights,
        s.number_of_reviews,
        s.last_review,
        s.reviews_per_month,
        s.calculated_host_listings_count,
        s.availability_365
    from source s
    left join {{ ref('dim_location') }} loc
        on s.neighbourhood_group = loc.neighbourhood_group
        and s.neighbourhood = loc.neighbourhood
    left join {{ ref('dim_room_type') }} rt
        on s.room_type = rt.room_type
)

select * from joined
