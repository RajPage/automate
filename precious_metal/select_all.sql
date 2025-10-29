SELECT
    price
FROM
    price_history
WHERE
    metal = ?
ORDER BY
    date ASC;