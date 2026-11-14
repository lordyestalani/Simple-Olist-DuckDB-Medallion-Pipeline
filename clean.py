import duckdb

result = duckdb.sql("""
    SELECT
        COUNT(*) AS item_rows,
        COUNT(o.order_id) AS matched_rows, COUNT(c.customer_id) AS matched_customer_rows
    FROM read_csv_auto('data/bronze/order_items/order_items_2018-01.csv') AS i
    LEFT JOIN read_csv_auto('data/bronze/orders/orders_2018-01.csv') AS o
        ON i.order_id = o.order_id
        LEFT JOIN read_csv_auto('data/bronze/reference/customers.csv') AS c
    ON o.customer_id = c.customer_id
""")

print(result.fetchall())