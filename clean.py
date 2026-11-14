import duckdb

result = duckdb.sql("""
    SELECT
        COUNT(*) AS item_rows,
        COUNT(o.order_id) AS matched_rows
    FROM read_csv_auto('data/bronze/order_items/order_items_2018-01.csv') AS i
    LEFT JOIN read_csv_auto('data/bronze/orders/orders_2018-01.csv') AS o
        ON i.order_id = o.order_id
""")

print(result.fetchall())