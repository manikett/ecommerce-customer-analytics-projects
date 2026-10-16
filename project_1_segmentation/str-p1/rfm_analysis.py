import pandas as pd

# Load RFM data
rfm = pd.read_csv("data/rfm.csv")

# -----------------------------
# RFM SCORING
# -----------------------------

# Recency:
# Lower recency = better customer
rfm["R_score"] = pd.qcut(
    rfm["recency"],
    q=5,
    labels=[5, 4, 3, 2, 1],
    duplicates="drop"
).astype(int)

# Frequency:
# Higher frequency = better customer
rfm["F_score"] = pd.qcut(
    rfm["frequency"].rank(method="first"),
    q=5,
    labels=[1, 2, 3, 4, 5]
).astype(int)

# Monetary:
# Higher spending = better customer
rfm["M_score"] = pd.qcut(
    rfm["monetary"],
    q=5,
    labels=[1, 2, 3, 4, 5],
    duplicates="drop"
).astype(int)

# Combined RFM score
rfm["RFM_score"] = (
    rfm["R_score"].astype(str)
    + rfm["F_score"].astype(str)
    + rfm["M_score"].astype(str)
)

# Numerical overall score
rfm["RFM_total"] = (
    rfm["R_score"]
    + rfm["F_score"]
    + rfm["M_score"]
)

# -----------------------------
# CUSTOMER SEGMENTS
# -----------------------------

def segment_customer(row):

    if row["RFM_total"] >= 13:
        return "Champions"

    elif row["RFM_total"] >= 10:
        return "Loyal Customers"

    elif row["RFM_total"] >= 8:
        return "Potential Loyalists"

    elif row["R_score"] <= 2 and row["F_score"] <= 2:
        return "At Risk"

    elif row["R_score"] == 1:
        return "Lost Customers"

    else:
        return "Needs Attention"


rfm["segment"] = rfm.apply(segment_customer, axis=1)

# -----------------------------
# SAVE FINAL CUSTOMER DATA
# -----------------------------

rfm.to_csv("data/customer_segments.csv", index=False)

print("RFM scoring completed!")
print(f"Total customers: {len(rfm)}")

print("\nSegment distribution:")
print(rfm["segment"].value_counts())

print("\nSample customers:")
print(
    rfm[
        [
            "customer_id",
            "recency",
            "frequency",
            "monetary",
            "RFM_score",
            "RFM_total",
            "segment"
        ]
    ].head(10)
)