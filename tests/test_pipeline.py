from datetime import date
from decimal import Decimal
from pathlib import Path
from shutil import copy2
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

import duckdb


class PipelineTest(unittest.TestCase):
    def test_rerunning_january_preserves_both_months(self):
        inputs = {
            "olist_orders_dataset.csv": (
                "order_id,customer_id,order_status,order_purchase_timestamp\n"
                "jan,c1,delivered,2018-01-31 23:59:59\n"
                "feb,c1,delivered,2018-02-01 00:00:00\n"
            ),
            "olist_order_items_dataset.csv": (
                "order_id,order_item_id,product_id,price,freight_value\n"
                "jan,1,p1,20.00,5.00\n"
                "feb,1,p1,40.00,8.00\n"
                "feb,2,p1,10.00,2.00\n"
            ),
            "olist_customers_dataset.csv": "customer_id,customer_state\nc1,SP\n",
            "olist_products_dataset.csv": "product_id,product_category_name\np1,livros\n",
            "product_category_name_translation.csv": (
                "product_category_name,product_category_name_english\nlivros,books\n"
            ),
        }
        project = Path(__file__).resolve().parents[1]

        with TemporaryDirectory() as folder:
            temp_project = Path(folder)
            for script in ("run.py", "backfill.py", "clean.py", "aggregate.py"):
                copy2(project / script, temp_project / script)

            source = temp_project / "data/source"
            source.mkdir(parents=True)
            for name, contents in inputs.items():
                (source / name).write_text(contents, encoding="utf-8")

            def run(month):
                subprocess.run(
                    [sys.executable, str(temp_project / "run.py"), month],
                    check=True,
                )

            def gold_rows():
                path = temp_project / "data/gold/monthly_category_state_sales.parquet"
                return duckdb.read_parquet(str(path)).order("purchase_month").fetchall()

            run("2018-01")
            bronze = temp_project / "data/bronze"
            for batch in (
                "orders/orders_2018-01.csv",
                "order_items/order_items_2018-01.csv",
            ):
                with self.subTest(batch=batch):
                    rows = duckdb.read_csv(str(bronze / batch)).project("order_id")
                    self.assertEqual(rows.fetchall(), [("jan",)])
            run("2018-02")
            silver_path = temp_project / "data/silver/order_items.parquet"
            silver_keys = (
                duckdb.read_parquet(str(silver_path))
                .project("order_id, order_item_id")
                .order("order_id, order_item_id")
                .fetchall()
            )
            self.assertEqual(silver_keys, [("feb", 1), ("feb", 2), ("jan", 1)])
            before = gold_rows()
            self.assertEqual(
                before,
                [
                    (date(2018, 1, 1), "books", "SP", Decimal("20.00"), Decimal("5.00")),
                    (date(2018, 2, 1), "books", "SP", Decimal("50.00"), Decimal("10.00")),
                ],
            )

            run("2018-01")
            self.assertEqual(gold_rows(), before)