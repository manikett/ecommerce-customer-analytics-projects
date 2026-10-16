import pandas as pd
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

# -----------------------------
# 1. LOAD TRANSACTIONS
# -----------------------------
transactions_file = DATA_DIR / "transactions.csv"

if not transactions_file.exists():
    raise FileNotFoundError("transactions.csv not found! Run final_extract.py first.")

transactions = pd.read_csv(transactions_file)
transactions["transaction_date"] = pd.to_datetime(transactions["transaction_date"])
transactions["customer_id"] = (
    transactions["customer_id"].astype(str).str.replace(r"\.0$", "", regex=True)
)

# -----------------------------
# 2. GENERATE RFM BASE DATA
# -----------------------------
# Reference point: dataset ki latest date
snapshot_date = transactions["transaction_date"].max()

rfm = (
    transactions.groupby("customer_id")
    .agg(
        recency=("transaction_date", lambda x: (snapshot_date - x.max()).days),
        frequency=("transaction_id", "nunique"),
        monetary=("item_revenue", "sum"),
        last_purchase_date=("transaction_date", "max")
    )
    .reset_index()
)

# Save base RFM
rfm.to_csv(DATA_DIR / "rfm.csv", index=False)
print("Base data/rfm.csv generated successfully.")

# -----------------------------
# 3. RFM SCORING
# -----------------------------
# Recency: Lower recency = Better score (5)
rfm["R_score"] = pd.qcut(
    rfm["recency"],
    q=5,
    labels=[5, 4, 3, 2, 1],
    duplicates="drop"
).astype(int)

# Frequency: Higher frequency = Better score (5)
rfm["F_score"] = pd.qcut(
    rfm["frequency"].rank(method="first"),
    q=5,
    labels=[1, 2, 3, 4, 5]
).astype(int)

# Monetary: Higher spend = Better score (5)
rfm["M_score"] = pd.qcut(
    rfm["monetary"],
    q=5,
    labels=[1, 2, 3, 4, 5],
    duplicates="drop"
).astype(int)

rfm["RFM_score"] = (
    rfm["R_score"].astype(str)
    + rfm["F_score"].astype(str)
    + rfm["M_score"].astype(str)
)

rfm["RFM_total"] = rfm["R_score"] + rfm["F_score"] + rfm["M_score"]

# -----------------------------
# 4. REFINED SEGMENTATION LOGIC
# -----------------------------
def segment_customer(row):
    r, f, m = row["R_score"], row["F_score"], row["M_score"]
    
    # Best customers: Active + frequent buyers
    if r >= 4 and f >= 4:
        return "Champions"
    # Steady repeat buyers
    elif r >= 3 and f >= 3:
        return "Loyal Customers"
    # Bought recently, but low frequency so far
    elif r >= 4 and f <= 2:
        return "Recent Customers"
    # Used to buy frequently, but haven't visited recently
    elif r <= 2 and f >= 3:
        return "At Risk"
    # Old buyers, low frequency, low engagement
    elif r <= 2 and f <= 2:
        return "Lost Customers"
    else:
        return "Needs Attention"

rfm["segment"] = rfm.apply(segment_customer, axis=1)

# -----------------------------
# 5. SAVE SEGMENTS
# -----------------------------
output_file = DATA_DIR / "customer_segments.csv"
rfm.to_csv(output_file, index=False)

print("Customer segments generated successfully.")
print(f"Total customers processed: {len(rfm):,}")
print("\nSegment distribution:")
print(rfm["segment"].value_counts())