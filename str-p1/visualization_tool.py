import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# E-COMMERCE VISUALIZATION TOOL
# ============================================================

# ------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------

transactions = pd.read_csv("data/transactions.csv")
rfm = pd.read_csv("data/rfm.csv")
segments = pd.read_csv("data/customer_segments.csv")

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

    plt.figure(figsize=(9, 6))

    plt.bar(data.index, data.values)

    plt.title("Customer Segment Distribution")
    plt.xlabel("Customer Segment")
    plt.ylabel("Number of Customers")

    plt.xticks(rotation=30, ha="right")

    show_chart()


# ============================================================
# 2. REVENUE BY SEGMENT
# ============================================================

def revenue_by_segment_chart():

    data = (
        transactions
        .merge(
            segments[["customer_id", "segment"]],
            on="customer_id",
            how="inner"
        )
        .groupby("segment")["item_revenue"]
        .sum()
        .sort_values(ascending=False)
    )

    plt.figure(figsize=(9, 6))

    plt.bar(data.index, data.values)

    plt.title("Revenue by Customer Segment")
    plt.xlabel("Customer Segment")
    plt.ylabel("Revenue")

    plt.xticks(rotation=30, ha="right")

    show_chart()


# ============================================================
# 3. MONTHLY REVENUE
# ============================================================

def monthly_revenue_chart():

    data = (
        transactions
        .assign(
            month=transactions[
                "transaction_date"
            ].dt.to_period("M")
        )
        .groupby("month")["item_revenue"]
        .sum()
    )

    data.index = data.index.astype(str)

    plt.figure(figsize=(9, 6))

    plt.plot(
        data.index,
        data.values,
        marker="o"
    )

    plt.title("Monthly Revenue Trend")
    plt.xlabel("Month")
    plt.ylabel("Revenue")

    plt.grid(True, alpha=0.3)

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

    plt.figure(figsize=(10, 7))

    plt.barh(
        data.index,
        data.values
    )

    plt.title("Top 10 Products by Revenue")
    plt.xlabel("Revenue")
    plt.ylabel("Product")

    show_chart()


# ============================================================
# 5. RFM ANALYSIS
# ============================================================

def rfm_chart():

    plt.figure(figsize=(9, 6))

    plt.scatter(
        rfm["recency"],
        rfm["monetary"],
        alpha=0.6
    )

    plt.title("Recency vs Monetary Value")
    plt.xlabel("Recency (Days)")
    plt.ylabel("Monetary Value")

    plt.grid(True, alpha=0.3)

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


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()