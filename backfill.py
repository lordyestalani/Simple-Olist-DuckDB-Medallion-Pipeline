from argparse import ArgumentParser
from datetime import date
from pathlib import Path
from shutil import copyfile

import duckdb

parser = ArgumentParser()
parser.add_argument("month", help="Purchase month in YYYY-MM format")
args = parser.parse_args()

try:
    month_start = date.fromisoformat(f"{args.month}-01")
except ValueError:
    parser.error("month must be a valid YYYY-MM value")

month = month_start.isoformat()[:7]
orders_path = f"data/bronze/orders/orders_{month}.csv"
items_path = f"data/bronze/order_items/order_items_{month}.csv"

duckdb.sql("""
    COPY (
        SELECT *
        FROM read_csv_auto(
            'data/source/olist_orders_dataset.csv', all_varchar = true
        )
        WHERE CAST(order_purchase_timestamp AS TIMESTAMP) >= CAST(? AS DATE)
          AND CAST(order_purchase_timestamp AS TIMESTAMP) < CAST(? AS DATE) + INTERVAL '1 month'
    ) TO (?) (FORMAT CSV, HEADER true)
""", params=[month_start, month_start, orders_path])

duckdb.sql("""
    COPY (
        SELECT *
        FROM read_csv_auto(
            'data/source/olist_order_items_dataset.csv', all_varchar = true
        )
        WHERE order_id IN (
            SELECT order_id
            FROM read_csv_auto(?, all_varchar = true)
        )
    ) TO (?) (FORMAT CSV, HEADER true)
""", params=[orders_path, items_path])

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