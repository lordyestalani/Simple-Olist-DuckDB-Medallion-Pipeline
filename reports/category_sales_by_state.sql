SELECT
    purchase_month,
    product_category,
    customer_state,
    merchandise_sales
FROM read_parquet('data/gold/monthly_category_state_sales.parquet')
WHERE purchase_month = DATE '2018-01-01'
  AND product_category = 'sports_leisure'
ORDER BY merchandise_sales DESC, customer_state;