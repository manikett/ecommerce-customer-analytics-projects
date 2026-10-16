from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# E-COMMERCE VISUALIZATION TOOL
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

# ------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------

transactions = pd.read_csv(DATA_DIR / "transactions.csv")
rfm = pd.read_csv(DATA_DIR / "rfm.csv")
segments = pd.read_csv(DATA_DIR / "customer_segments.csv")

transactions["transaction_date"] = pd.to_datetime(
    transactions["transaction_date"]
)

# Keep customer IDs consistent
for df in [transactions, rfm, segments]:
    df["customer_id"] = (
        df["customer_id"]
        .astype(str)
        .str.replace(r"\.0$", "", regex=True)
    )


# ------------------------------------------------------------
# HELPER
# ------------------------------------------------------------

def show_chart():
    plt.tight_layout()
    plt.show()
    plt.close()


# ============================================================
# 1. CUSTOMER SEGMENTS
# ============================================================

def customer_segments_chart():
    data = segments["segment"].value_counts()

    plt.figure(figsize=(9, 5))
    bars = plt.bar(data.index, data.values, color="#2b5c8f")

    plt.title("Customer Segment Distribution", fontsize=14, pad=12)
    plt.xlabel("Customer Segment", fontsize=11)
    plt.ylabel("Number of Customers", fontsize=11)
    plt.xticks(rotation=25, ha="right")
    plt.grid(axis="y", linestyle="--", alpha=0.5)

    # Bar labels
    for bar in bars:
        yval = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            yval + 10,
            f"{int(yval):,}",
            ha="center",
            va="bottom",
            fontsize=9
        )

    show_chart()


# ============================================================
# 2. REVENUE BY SEGMENT
# ============================================================

def revenue_by_segment_chart():
    data = (
        segments.groupby("segment")["monetary"]
        .sum()
        .sort_values(ascending=False)
    )

    plt.figure(figsize=(9, 5))
    plt.bar(data.index, data.values, color="#2e7d32")

    plt.title("Total Revenue by Customer Segment ($)", fontsize=14, pad=12)
    plt.xlabel("Customer Segment", fontsize=11)
    plt.ylabel("Revenue ($)", fontsize=11)
    plt.xticks(rotation=25, ha="right")
    plt.grid(axis="y", linestyle="--", alpha=0.5)

    show_chart()


# ============================================================
# 3. MONTHLY REVENUE
# ============================================================

def monthly_revenue_chart():
    data = (
        transactions
        .assign(month=transactions["transaction_date"].dt.to_period("M"))
        .groupby("month")["item_revenue"]
        .sum()
    )

    data.index = data.index.astype(str)

    plt.figure(figsize=(9, 5))
    plt.plot(data.index, data.values, marker="o", color="#d32f2f", linewidth=2)

    plt.title("Monthly Revenue Trend ($)", fontsize=14, pad=12)
    plt.xlabel("Month", fontsize=11)
    plt.ylabel("Revenue ($)", fontsize=11)
    plt.xticks(rotation=35, ha="right")
    plt.grid(True, linestyle="--", alpha=0.5)

    show_chart()


# ============================================================
# 4. TOP PRODUCTS
# ============================================================

def top_products_chart():
    data = (
        transactions
        .groupby("product_name")["item_revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .sort_values()
    )

    plt.figure(figsize=(10, 6))
    plt.barh(data.index, data.values, color="#ef6c00")

    plt.title("Top 10 Products by Revenue ($)", fontsize=14, pad=12)
    plt.xlabel("Revenue ($)", fontsize=11)
    plt.ylabel("Product", fontsize=11)
    plt.grid(axis="x", linestyle="--", alpha=0.5)

    show_chart()


# ============================================================
# 5. RFM ANALYSIS
# ============================================================

def rfm_chart():
    plt.figure(figsize=(9, 5))
    plt.scatter(
        rfm["recency"],
        rfm["monetary"],
        alpha=0.5,
        color="#6a1b9a",
        edgecolors="none"
    )

    plt.title("Recency vs Monetary Value", fontsize=14, pad=12)
    plt.xlabel("Recency (Days)", fontsize=11)
    plt.ylabel("Monetary Value ($)", fontsize=11)
    plt.grid(True, linestyle="--", alpha=0.5)

    show_chart()


# ============================================================
# MAIN MENU
# ============================================================

def main():
    while True:
        print("\n" + "=" * 60)
        print("          E-COMMERCE VISUALIZATIONS")
        print("=" * 60)

        print("\n1. Customer Segments")
        print("2. Revenue by Segment")
        print("3. Monthly Revenue")
        print("4. Top Products")
        print("5. RFM Analysis")
        print("0. Back to Main Menu")

        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            customer_segments_chart()
        elif choice == "2":
            revenue_by_segment_chart()
        elif choice == "3":
            monthly_revenue_chart()
        elif choice == "4":
            top_products_chart()
        elif choice == "5":
            rfm_chart()
        elif choice == "0":
            print("\nReturning to Main Menu...")
            break
        else:
            print("\nInvalid choice. Please try again.")


if __name__ == "__main__":
    main()