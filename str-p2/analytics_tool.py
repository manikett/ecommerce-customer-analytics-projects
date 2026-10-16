from pathlib import Path
import pandas as pd

# ============================================================
# E-COMMERCE CUSTOMER ANALYTICS
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
# HELPER FUNCTIONS
# ------------------------------------------------------------

def heading(title):
    print("\n" + "=" * 60)
    print(f"{title:^60}")
    print("=" * 60)


def money(value):
    return f"${value:,.2f}"


# ============================================================
# 1. CUSTOMER OVERVIEW
# ============================================================

def customer_overview():
    heading("CUSTOMER OVERVIEW")

    total_customers = rfm["customer_id"].nunique()
    repeat_customers = (rfm["frequency"] > 1).sum()
    one_time_customers = (rfm["frequency"] == 1).sum()

    repeat_rate = (
        repeat_customers / total_customers * 100
        if total_customers > 0
        else 0
    )

    average_spend = rfm["monetary"].mean()
    average_frequency = rfm["frequency"].mean()

    print("\nCUSTOMER METRICS")
    print("-" * 60)
    print(f"Total Customers       : {total_customers:,}")
    print(f"Repeat Customers      : {repeat_customers:,}")
    print(f"One-Time Customers    : {one_time_customers:,}")
    print(f"Repeat Customer Rate  : {repeat_rate:.2f}%")
    print(f"Average Customer Spend: {money(average_spend)}")
    print(f"Average Purchase Count: {average_frequency:.2f}")


# ============================================================
# 2. CUSTOMER LOOKUP
# ============================================================

def customer_lookup():
    heading("CUSTOMER LOOKUP")

    customer_id = input("\nEnter Customer ID: ").strip()

    if not customer_id:
        print("\nCustomer ID cannot be empty.")
        return

    customer = rfm[rfm["customer_id"] == customer_id]

    if customer.empty:
        print(f"\nCustomer ID '{customer_id}' not found.")
        return

    customer = customer.iloc[0]
    segment_data = segments[segments["customer_id"] == customer_id]

    segment = (
        segment_data["segment"].iloc[0]
        if not segment_data.empty
        else "N/A"
    )

    print("\nCUSTOMER PROFILE")
    print("-" * 60)
    print(f"Customer ID    : {customer_id}")
    print(f"Segment        : {segment}")
    print(f"Recency        : {int(customer['recency'])} days")
    print(f"Frequency      : {int(customer['frequency'])} purchases")
    print(f"Monetary Value : {money(customer['monetary'])}")
    print(
        f"Last Purchase  : "
        f"{pd.to_datetime(customer['last_purchase_date']).strftime('%Y-%m-%d')}"
    )

    history = transactions[transactions["customer_id"] == customer_id].copy()

    if history.empty:
        return

    print("\nPURCHASE HISTORY")
    print("-" * 60)

    history_summary = (
        history
        .groupby(["transaction_id", "transaction_date"])
        .agg(
            units=("quantity", "sum"),
            revenue=("item_revenue", "sum")
        )
        .reset_index()
        .sort_values("transaction_date", ascending=False)
    )

    print(history_summary.to_string(index=False))


# ============================================================
# 3. SALES OVERVIEW
# ============================================================

def sales_overview():
    heading("SALES OVERVIEW")

    total_revenue = transactions["item_revenue"].sum()
    total_units = transactions["quantity"].sum()
    total_transactions = transactions["transaction_id"].nunique()
    total_customers = transactions["customer_id"].nunique()

    average_order_value = (
        total_revenue / total_transactions
        if total_transactions > 0
        else 0
    )

    print("\nSALES METRICS")
    print("-" * 60)
    print(f"Total Revenue       : {money(total_revenue)}")
    print(f"Total Units Sold    : {total_units:,}")
    print(f"Total Transactions  : {total_transactions:,}")
    print(f"Unique Customers    : {total_customers:,}")
    print(f"Average Order Value : {money(average_order_value)}")

    print("\nDATA PERIOD")
    print("-" * 60)
    first_date = transactions["transaction_date"].min()
    last_date = transactions["transaction_date"].max()
    print(f"From : {first_date.strftime('%Y-%m-%d')}")
    print(f"To   : {last_date.strftime('%Y-%m-%d')}")


# ============================================================
# 4. MONTHLY SALES
# ============================================================

def monthly_sales():
    heading("MONTHLY SALES")

    monthly = (
        transactions
        .assign(month=transactions["transaction_date"].dt.strftime("%Y-%m"))
        .groupby("month")
        .agg(
            revenue=("item_revenue", "sum"),
            units=("quantity", "sum"),
            transactions=("transaction_id", "nunique"),
            customers=("customer_id", "nunique")
        )
        .reset_index()
        .sort_values("month")
    )

    monthly["revenue"] = monthly["revenue"].map(lambda x: f"${x:,.2f}")
    print()
    print(monthly.to_string(index=False))


# ============================================================
# 5. TOP PRODUCTS
# ============================================================

def top_products():
    heading("TOP PRODUCTS")
    print("\n1. By Revenue")
    print("2. By Units Sold")
    print("0. Back")

    choice = input("\nChoose an option: ").strip()

    if choice == "0":
        return

    if choice == "1":
        result = (
            transactions
            .groupby("product_name")
            .agg(
                units=("quantity", "sum"),
                revenue=("item_revenue", "sum")
            )
            .reset_index()
            .sort_values("revenue", ascending=False)
            .head(10)
        )
        result["revenue"] = result["revenue"].map(lambda x: f"${x:,.2f}")
        print("\nTOP 10 PRODUCTS BY REVENUE")
        print("-" * 60)
        print(result.to_string(index=False))

    elif choice == "2":
        result = (
            transactions
            .groupby("product_name")
            .agg(
                units=("quantity", "sum"),
                revenue=("item_revenue", "sum")
            )
            .reset_index()
            .sort_values("units", ascending=False)
            .head(10)
        )
        result["revenue"] = result["revenue"].map(lambda x: f"${x:,.2f}")
        print("\nTOP 10 PRODUCTS BY UNITS SOLD")
        print("-" * 60)
        print(result.to_string(index=False))
    else:
        print("\nInvalid choice.")


# ============================================================
# 6. RFM SUMMARY
# ============================================================

def rfm_summary():
    heading("RFM SUMMARY")
    print("\nRFM METRICS")
    print("-" * 60)
    print(f"Customers        : {len(rfm):,}")
    print(f"Average Recency  : {rfm['recency'].mean():.2f} days")
    print(f"Average Frequency: {rfm['frequency'].mean():.2f}")
    print(f"Average Monetary : {money(rfm['monetary'].mean())}")

    print("\nTOP 10 CUSTOMERS BY MONETARY VALUE")
    print("-" * 60)

    top = (
        rfm
        .sort_values("monetary", ascending=False)
        .head(10)[["customer_id", "recency", "frequency", "monetary"]]
        .copy()
    )
    top["monetary"] = top["monetary"].map(lambda x: f"${x:,.2f}")
    print(top.to_string(index=False))


# ============================================================
# 7. SEGMENT PERFORMANCE
# ============================================================

def segment_performance():
    heading("CUSTOMER SEGMENT PERFORMANCE")

    summary = (
        segments
        .groupby("segment")
        .agg(
            customers=("customer_id", "nunique"),
            avg_recency=("recency", "mean"),
            avg_frequency=("frequency", "mean"),
            avg_monetary=("monetary", "mean"),
            revenue=("monetary", "sum")
        )
        .reset_index()
        .sort_values("revenue", ascending=False)
    )

    summary["avg_recency"] = summary["avg_recency"].round(1)
    summary["avg_frequency"] = summary["avg_frequency"].round(2)
    summary["avg_monetary"] = summary["avg_monetary"].map(lambda x: f"${x:,.2f}")
    summary["revenue"] = summary["revenue"].map(lambda x: f"${x:,.2f}")

    print()
    print(summary.to_string(index=False))


# ============================================================
# SUB-MENUS & MAIN
# ============================================================

def customer_menu():
    while True:
        heading("CUSTOMER ANALYSIS")
        print("1. Customer Overview")
        print("2. Customer Lookup")
        print("0. Back to Main Menu")

        choice = input("\nChoose an option: ").strip()
        if choice == "1":
            customer_overview()
        elif choice == "2":
            customer_lookup()
        elif choice == "0":
            return
        else:
            print("\nInvalid choice.")


def sales_menu():
    while True:
        heading("SALES ANALYSIS")
        print("1. Sales Overview")
        print("2. Monthly Sales")
        print("3. Top Products")
        print("0. Back to Main Menu")

        choice = input("\nChoose an option: ").strip()
        if choice == "1":
            sales_overview()
        elif choice == "2":
            monthly_sales()
        elif choice == "3":
            top_products()
        elif choice == "0":
            return
        else:
            print("\nInvalid choice.")


def segmentation_menu():
    while True:
        heading("CUSTOMER SEGMENTATION")
        print("1. RFM Summary")
        print("2. Segment Performance")
        print("0. Back to Main Menu")

        choice = input("\nChoose an option: ").strip()
        if choice == "1":
            rfm_summary()
        elif choice == "2":
            segment_performance()
        elif choice == "0":
            return
        else:
            print("\nInvalid choice.")


def main():
    while True:
        print("\n" + "=" * 60)
        print("       E-COMMERCE CUSTOMER ANALYTICS")
        print("=" * 60)
        print("\n1. Customer Analysis")
        print("2. Sales Analysis")
        print("3. Customer Segmentation")
        print("0. Exit")

        choice = input("\nChoose an option: ").strip()
        if choice == "1":
            customer_menu()
        elif choice == "2":
            sales_menu()
        elif choice == "3":
            segmentation_menu()
        elif choice == "0":
            print("\nThank you for using the Analytics Tool!")
            break
        else:
            print("\nInvalid choice. Please try again.")


if __name__ == "__main__":
    main()