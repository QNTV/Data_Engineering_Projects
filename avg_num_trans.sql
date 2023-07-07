{{ config(materialized='table') }}

WITH ga_data AS (
    Select 
        date,
        fullVisitorId,
        SUM (transactions) AS total_transactions_per_user
    FROM
        {{ source('raw','ga_data_raw') }}
    WHERE
    transactions is NOT NULL

    Group BY
        date,
        fullVisitorId    
)

SELECT
    date,
    (sum (total_transactions_per_user) / count (distinct fullVisitorId)) AS average_transactions_per_user
FROM
    ga_data
GROUP BY
    DATE