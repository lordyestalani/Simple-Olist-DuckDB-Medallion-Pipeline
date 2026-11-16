import duckdb

result = duckdb.sql("""
    SELECT
    i.order_id,
    i.order_item_id,
    CAST(DATE_TRUNC('month', o.order_purchase_timestamp) AS DATE) AS purchase_month,
    o.order_status,
    c.customer_state,
    COALESCE(t.product_category_name_english, p.product_category_name, 'unknown') AS product_category,
    CAST(i.price AS DECIMAL(12, 2)) AS price,
    CAST(i.freight_value AS DECIMAL(12, 2)) AS freight_value
    FROM read_csv_auto('data/bronze/order_items/order_items_*.csv') AS i
    LEFT JOIN read_csv_auto('data/bronze/orders/orders_*.csv') AS o
        ON i.order_id = o.order_id
        LEFT JOIN read_csv_auto('data/bronze/reference/customers.csv') AS c
    ON o.customer_id = c.customer_id LEFT JOIN read_csv_auto('data/bronze/reference/products.csv') AS p
    ON i.product_id = p.product_id
    LEFT JOIN read_csv_auto('data/bronze/reference/category_translations.csv') AS t
    ON p.product_category_name = t.product_category_name
""")

output_path = "data/silver/order_items.parquet"
result.write_parquet(output_path)

silver = duckdb.read_parquet(output_path)
print(silver.query("items", """
    SELECT purchase_month, COUNT(*) AS item_rows
    FROM items
    GROUP BY purchase_month
    ORDER BY purchase_month
""").fetchall())