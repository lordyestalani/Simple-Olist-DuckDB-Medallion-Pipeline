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

print(summary.count("*").fetchall())