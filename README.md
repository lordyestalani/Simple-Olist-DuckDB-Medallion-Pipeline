# Olist Sales and Freight Pipeline

A local data engineering demo built with Python, DuckDB SQL, and Parquet. It turns five CSVs from the Brazilian E-Commerce Public Dataset by Olist into reports on product sales and freight charges.

The source is a fixed snapshot. The pipeline simulates a historical backfill by selecting one purchase month at a time. It replaces that month’s Bronze batches on rerun, then rebuilds Silver and Gold from all months currently loaded in Bronze.

## Source data

The original CSVs are in [`data/source/`](data/source/).

| CSV | What the pipeline uses |
| --- | --- |
| `olist_orders_dataset.csv` | Order ID, purchase timestamp, order status, and customer ID |
| `olist_order_items_dataset.csv` | Order and item IDs, product ID, item price, and freight charge |
| `olist_customers_dataset.csv` | Customer state |
| `olist_products_dataset.csv` | Product category |
| `product_category_name_translation.csv` | English category labels |

## Pipeline

| Layer | Script | Transformation and output |
| --- | --- | --- |
| Bronze | [`backfill.py`](backfill.py) | Selects orders from the start of the requested month up to the start of the next month. Uses those order IDs to select the corresponding items. Writes monthly CSVs under `data/bronze/orders/` and `data/bronze/order_items/`. Copies the three reference files into `data/bronze/reference/` on the first run. |
| Silver | [`clean.py`](clean.py) | Reads all Bronze batches and left joins orders, customers, products, and category translations to the items. The intended grain is one row per `(order_id, order_item_id)`. Stores the purchase month as a date and monetary values as decimals in `data/silver/order_items.parquet`. |
| Gold | [`aggregate.py`](aggregate.py) | Sums merchandise sales and freight charges for delivered items. Writes one row per purchase month, product category, and customer state to `data/gold/monthly_category_state_sales.parquet`. |

[`run.py`](run.py) accepts a purchase month in `YYYY-MM` format and runs the three stages in order. Silver uses the English category label when available, falls back to the original label, and uses `unknown` when the category is missing.

## Business questions

| Question | SQL report | Verified January 2018 result |
| --- | --- | --- |
| Which categories generate the most merchandise sales each month? | [Monthly category sales](reports/monthly_category_sales.sql) | `sports_leisure` led at R$86,172.83. |
| Which customer states drive sales for a selected month and category? | [Category sales by state](reports/category_sales_by_state.sql) | For `sports_leisure`, São Paulo (SP) led at R$30,686.32. |
| Which categories have the highest freight charges relative to merchandise sales? | [Freight share by category](reports/freight_share_by_category.sql) | `dvds_blu_ray` led at 93.94%. |

Merchandise sales sum item prices in Brazilian reais (BRL). The freight report divides total freight charges by total merchandise sales after summing both across customer states.

## Verified backfill results

| Purchase month | Bronze orders | Silver items | Gold rows | Merchandise sales | Freight charges |
| --- | ---: | ---: | ---: | ---: | ---: |
| January 2018 | 7,269 | 8,208 | 695 | R$924,645.00 | R$153,242.46 |
| February 2018 | 6,728 | 7,672 | 651 | R$826,437.13 | R$139,731.28 |
| March 2018 | 7,211 | 8,217 | 680 | R$953,356.25 | R$167,241.99 |

After loading all three months, rerunning January preserved the Silver and Gold row counts and every value in the 2,026 Gold rows. The Gold comparison sorted by month, category, and state before comparing the rows.

The [automated pipeline test](tests/test_pipeline.py) uses small CSVs in a temporary project. It verifies which orders and items land in the January Bronze batches, checks that Silver preserves each item key exactly once, and compares Gold sales and freight against exact expected totals. It also verifies that rerunning January preserves the January and February Gold rows.

## Milestones

- [x] Build the January pipeline from the source CSVs through Gold and verify three SQL reports.
- [x] Add a monthly runner, backfill February and March, and verify the January rerun.
- [x] Add an automated rerun test with sample CSVs.
- [x] Check the month boundary in the January Bronze orders and items batches.
- [x] Check Silver join cardinality and exact Gold sales and freight values.
- [ ] **Next milestone:** Package the pipeline in Docker and verify it from a clean checkout.
- [ ] Expand this README with tested setup, pipeline, report, and test commands.

Optional follow-ups include scheduling monthly backfills with an Airflow DAG and exploring the Gold data in Power BI.

## Data attribution

The source CSVs are from the [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce), licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/). The pipeline derives monthly Bronze batches and Silver and Gold Parquet files from that data.
