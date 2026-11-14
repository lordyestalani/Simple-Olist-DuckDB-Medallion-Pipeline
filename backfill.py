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