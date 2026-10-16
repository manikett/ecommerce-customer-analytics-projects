import os
from pathlib import Path
from dotenv import load_dotenv
from google.cloud import bigquery
import pandas as pd

# Load environment variable
load_dotenv()
PROJECT_ID = os.getenv("BIGQUERY_PROJECT_ID")

if not PROJECT_ID:
    raise ValueError("BIGQUERY_PROJECT_ID missing in .env file!")

client = bigquery.Client(project=PROJECT_ID)

query = """
SELECT
    user_pseudo_id AS customer_id,
    ecommerce.transaction_id AS transaction_id,
    PARSE_DATE('%Y%m%d', event_date) AS transaction_date,
    item.item_id AS product_id,
    item.item_name AS product_name,
    item.quantity AS quantity,
    item.item_revenue AS item_revenue
FROM
    `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`,
    UNNEST(items) AS item
WHERE
    event_name = 'purchase'
    AND item.quantity IS NOT NULL
    AND item.item_revenue IS NOT NULL
    AND item.item_id != '(not set)'
    AND ecommerce.transaction_id IS NOT NULL
"""

print("Fetching data from BigQuery...")

df = client.query(query).to_dataframe()

print(f"Records fetched: {len(df):,}")
print(f"Customers: {df['customer_id'].nunique():,}")

BASE_DIR = Path(__file__).resolve().parent
output_dir = BASE_DIR / "data"
output_dir.mkdir(parents=True, exist_ok=True)

output_file = output_dir / "transactions.csv"
df.to_csv(output_file, index=False)

print(f"Dataset saved to: {output_file}")