from argparse import ArgumentParser
from pathlib import Path
import subprocess
import sys

parser = ArgumentParser()
parser.add_argument("month", help="Purchase month in YYYY-MM format")
args = parser.parse_args()

project_dir = Path(__file__).resolve().parent

for folder in (
    "data/bronze/orders",
    "data/bronze/order_items",
    "data/bronze/reference",
    "data/silver",
    "data/gold",
):
    (project_dir / folder).mkdir(parents=True, exist_ok=True)

subprocess.run([sys.executable, "backfill.py", args.month], cwd=project_dir, check=True)
subprocess.run([sys.executable, "clean.py"], cwd=project_dir, check=True)
subprocess.run([sys.executable, "aggregate.py"], cwd=project_dir, check=True)