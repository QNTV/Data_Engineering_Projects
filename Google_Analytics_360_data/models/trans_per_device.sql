{{ config(materialized='table') }}

SELECT

    date,
    browser,
    SUM (transactions) AS total_transactons
FROM

    {{source('raw', 'ga_data_raw')}}
GROUP BY

    date,
    browser

ORDER BY
    total_transactons DESC