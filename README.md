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

## Reproduce the demo

Run these commands in PowerShell from the root of a fresh checkout with Docker running. Build the image and copy the five source CSVs to a temporary data folder.

```powershell
docker build -t olist-pipeline .

$demoData = Join-Path ([System.IO.Path]::GetTempPath()) ("olist-docker-" + [guid]::NewGuid())
New-Item -ItemType Directory -Path $demoData | Out-Null
Copy-Item -LiteralPath .\data\source -Destination (Join-Path $demoData "source") -Recurse

docker run --rm --mount "type=bind,source=$demoData,target=/app/data" olist-pipeline 2018-01
Get-ChildItem -LiteralPath (Join-Path $demoData "gold") -Name
```

The container writes Bronze, Silver, and Gold to `$demoData`. A clean-checkout run produced 8,208 Silver items, 695 Gold rows, and `monthly_category_state_sales.parquet` in the Gold folder. To reproduce the three-month demo, run the same command with `2018-02` and `2018-03`, keeping the same `$demoData` folder.

Run the automated test in the same image. The test creates its own source CSVs.

```powershell
docker run --rm --entrypoint python olist-pipeline -m unittest discover -s tests -v
```

### Query the reports locally

With Python 3.11 available, create an environment and install the same DuckDB release used in Docker.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

From the repository root, preview three rows from the report using the Gold file committed with the demo. Change the SQL filename to run either of the other reports.

```powershell
.\.venv\Scripts\python.exe -c "from pathlib import Path; import duckdb; print(duckdb.sql(Path('reports/monthly_category_sales.sql').read_text(encoding='utf-8-sig')).limit(3).fetchall())"
```

## Milestones

- [x] Build the January pipeline from the source CSVs through Gold and verify three SQL reports.
- [x] Add a monthly runner, backfill February and March, and verify the January rerun.
- [x] Add an automated rerun test with sample CSVs.
- [x] Check the month boundary in the January Bronze orders and items batches.
- [x] Check Silver join cardinality and exact Gold sales and freight values.
- [x] Package the pipeline in Docker, run the test in the image, and verify January from a clean checkout.
- [x] Document how to build the image, run a backfill, run the test, and query the reports.

Optional follow-ups include scheduling monthly backfills with an Airflow DAG and exploring the Gold data in Power BI.

## Data attribution

The source CSVs are from the [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce), licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/). The pipeline derives monthly Bronze batches and Silver and Gold Parquet files from that data.
