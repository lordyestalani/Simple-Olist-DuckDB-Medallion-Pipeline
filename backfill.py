from pathlib import Path
from shutil import copyfile
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

source_dir = Path("data/source")
reference_dir = Path("data/bronze/reference")

reference_files = {
    "olist_customers_dataset.csv": "customers.csv",
    "olist_products_dataset.csv": "products.csv",
    "product_category_name_translation.csv": "category_translations.csv",
}

for source_name, bronze_name in reference_files.items():
    destination = reference_dir / bronze_name
    if not destination.exists():
        copyfile(source_dir / source_name, destination)