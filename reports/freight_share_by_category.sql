SELECT
    purchase_month,
    product_category,
    ROUND(100 * SUM(freight_charges) / NULLIF(SUM(merchandise_sales), 0), 2)
        AS freight_pct
FROM read_parquet('data/gold/monthly_category_state_sales.parquet')
GROUP BY purchase_month, product_category
ORDER BY purchase_month, freight_pct DESC NULLS LAST, product_category;