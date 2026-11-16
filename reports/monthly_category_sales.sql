SELECT
    purchase_month,
    product_category,
    SUM(merchandise_sales) AS merchandise_sales
FROM read_parquet('data/gold/monthly_category_state_sales.parquet')
GROUP BY purchase_month, product_category
ORDER BY purchase_month, merchandise_sales DESC, product_category;