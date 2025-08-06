{{ config(materialized='table') }}

with source as (
    
    SELECT 
        INITCAP(name) AS nombre,
        height AS altura,
        weight AS peso,
        INITCAP(types) AS tipos
    FROM {{ ref('stg_pokemon') }}

),

deduplicated as (
    select distinct * from source
)

select * from deduplicated