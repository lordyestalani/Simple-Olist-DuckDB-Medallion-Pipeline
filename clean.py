import duckdb

result = duckdb.sql("""
    SELECT
        COUNT(*) AS item_rows,
        COUNT(o.order_id) AS matched_rows, COUNT(c.customer_id) AS matched_customer_rows, COUNT(p.product_id) AS matched_product_rows, COUNT(t.product_category_name_english) AS translated_category_rows
    FROM read_csv_auto('data/bronze/order_items/order_items_2018-01.csv') AS i
    LEFT JOIN read_csv_auto('data/bronze/orders/orders_2018-01.csv') AS o
        ON i.order_id = o.order_id
        LEFT JOIN read_csv_auto('data/bronze/reference/customers.csv') AS c
    ON o.customer_id = c.customer_id LEFT JOIN read_csv_auto('data/bronze/reference/products.csv') AS p
    ON i.product_id = p.product_id
    LEFT JOIN read_csv_auto('data/bronze/reference/category_translations.csv') AS t
    ON p.product_category_name = t.product_category_name
""")

print(result.fetchall())