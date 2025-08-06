{{ config(materialized='view') }}

select
    name, height, weight, types
from {{ source('public', 'pokemon') }}