import os
from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()
PROJECT_ID = os.getenv("BIGQUERY_PROJECT_ID")

client = bigquery.Client(project=PROJECT_ID)

query = """
SELECT
    COUNT(*) AS total_purchase_events
FROM
    `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
WHERE
    event_name = 'purchase'
"""

result = client.query(query)

for row in result:
    print("Total purchase events:", row.total_purchase_events)