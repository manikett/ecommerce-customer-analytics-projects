from google.cloud import bigquery

client = bigquery.Client(project="boxwood-pilot-508218-n5")

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