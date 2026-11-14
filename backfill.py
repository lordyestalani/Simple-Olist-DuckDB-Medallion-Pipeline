import duckdb

duckdb.sql("""
    COPY (
        SELECT *
        FROM read_csv_auto(
            'data/source/olist_orders_dataset.csv',
            all_varchar = true
        )
        WHERE CAST(order_purchase_timestamp AS TIMESTAMP) >= TIMESTAMP '2018-01-01'
          AND CAST(order_purchase_timestamp AS TIMESTAMP) <  TIMESTAMP '2018-02-01'
    ) TO 'data/bronze/orders/orders_2018-01.csv' (FORMAT CSV, HEADER true)
""")

duckdb.sql("""
    COPY (
        SELECT *
        FROM read_csv_auto(
            'data/source/olist_order_items_dataset.csv',
            all_varchar = true
        )
        WHERE order_id IN (
            SELECT order_id
            FROM read_csv_auto(
                'data/bronze/orders/orders_2018-01.csv',
                all_varchar = true
            )
        )
    ) TO 'data/bronze/order_items/order_items_2018-01.csv'
    (FORMAT CSV, HEADER true)
""")