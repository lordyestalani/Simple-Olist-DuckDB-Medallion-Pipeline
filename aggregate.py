import duckdb

summary = duckdb.sql("""
    SELECT
        purchase_month,
        product_category,
        customer_state,
        SUM(price) AS merchandise_sales,
        SUM(freight_value) AS freight_charges
    FROM read_parquet('data/silver/order_items.parquet')
    WHERE order_status = 'delivered'
    GROUP BY purchase_month, product_category, customer_state
""")

output_path = "data/gold/monthly_category_state_sales.parquet"
summary.write_parquet(output_path)

gold = duckdb.read_parquet(output_path)
print(gold.query("sales", """
    SELECT purchase_month, COUNT(*) AS summary_rows
    FROM sales
    GROUP BY purchase_month
    ORDER BY purchase_month
""").fetchall())