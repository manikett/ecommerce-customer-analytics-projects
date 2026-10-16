from pathlib import Path
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# Page Setup
st.set_page_config(page_title="Executive Customer Analytics", layout="wide", initial_sidebar_state="expanded")

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

@st.cache_data
def load_data():
    transactions = pd.read_csv(DATA_DIR / "transactions.csv")
    rfm = pd.read_csv(DATA_DIR / "rfm.csv")
    segments = pd.read_csv(DATA_DIR / "customer_segments.csv")

    transactions["transaction_date"] = pd.to_datetime(transactions["transaction_date"])
    for df in [transactions, rfm, segments]:
        df["customer_id"] = df["customer_id"].astype(str).str.replace(r"\.0$", "", regex=True)
    return transactions, rfm, segments

try:
    transactions, rfm, segments = load_data()
except Exception as e:
    st.error("Data files load nahi ho paaye. Pehle 'python run_project.py' run karo.")
    st.stop()

# -----------------------------
# SIDEBAR FILTERS (Point 4: Dynamic Filters)
# -----------------------------
st.sidebar.title("🎛️ Dashboard Filters")

min_date = transactions["transaction_date"].min().date()
max_date = transactions["transaction_date"].max().date()

date_range = st.sidebar.date_input(
    "Select Transaction Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered_trans = transactions[
        (transactions["transaction_date"].dt.date >= start_date) &
        (transactions["transaction_date"].dt.date <= end_date)
    ]
else:
    filtered_trans = transactions

# Title
st.title("🛍️ E-Commerce Customer Analytics Platform")

# Top KPI Metrics
col1, col2, col3, col4 = st.columns(4)
total_revenue = filtered_trans["item_revenue"].sum()
total_customers = rfm["customer_id"].nunique()
total_orders = filtered_trans["transaction_id"].nunique()
avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
repeat_rate = ((rfm["frequency"] > 1).sum() / total_customers) * 100

col1.metric("Total Revenue", f"${total_revenue:,.2f}")
col2.metric("Total Customers", f"{total_customers:,}")
col3.metric("Avg Order Value", f"${avg_order_value:,.2f}")
col4.metric("Repeat Customer Rate", f"{repeat_rate:.1f}%")

st.markdown("---")

# Navigation Tabs (All 4 Features Included)
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview & Trends", 
    "🗓️ Cohort Retention", 
    "💰 CLV Prediction",
    "💡 Business Playbook", 
    "🔍 Customer 360°"
])

# -----------------------------
# TAB 1: OVERVIEW & TRENDS
# -----------------------------
with tab1:
    plt.style.use("dark_background")
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Customer Segment Distribution")
        seg_counts = segments["segment"].value_counts()
        fig, ax = plt.subplots(figsize=(6, 3.8))
        fig.patch.set_facecolor("#0e1117")
        ax.set_facecolor("#0e1117")

        bars = ax.bar(seg_counts.index, seg_counts.values, color="#4da6ff")
        ax.set_ylabel("Customers", color="white")
        plt.xticks(rotation=30, ha="right", color="white", fontsize=9)
        plt.yticks(color="white")
        ax.grid(axis="y", linestyle="--", alpha=0.25)
        
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval + 15, f"{int(yval)}", ha="center", va="bottom", color="white", fontsize=8)

        st.pyplot(fig)
        plt.close()

    with c2:
        st.subheader("Monthly Revenue Trend")
        monthly = (
            filtered_trans
            .assign(month=filtered_trans["transaction_date"].dt.to_period("M"))
            .groupby("month")["item_revenue"].sum()
        )
        monthly.index = monthly.index.astype(str)

        fig, ax = plt.subplots(figsize=(6, 3.8))
        fig.patch.set_facecolor("#0e1117")
        ax.set_facecolor("#0e1117")

        ax.plot(monthly.index, monthly.values, marker="o", color="#ff4b4b", linewidth=2)
        ax.set_ylabel("Revenue ($)", color="white")
        plt.xticks(rotation=30, ha="right", color="white", fontsize=9)
        plt.yticks(color="white")
        ax.yaxis.set_major_formatter(lambda x, pos: f"${int(x*1e-3)}k")
        ax.grid(True, linestyle="--", alpha=0.25)

        st.pyplot(fig)
        plt.close()

    st.subheader("Segment Performance Breakdown")
    summary = (
        segments.groupby("segment").agg(
            customers=("customer_id", "nunique"),
            avg_recency=("recency", "mean"),
            avg_frequency=("frequency", "mean"),
            avg_monetary=("monetary", "mean"),
            revenue=("monetary", "sum")
        ).reset_index().sort_values("revenue", ascending=False)
    )
    summary["avg_recency"] = summary["avg_recency"].round(1)
    summary["avg_frequency"] = summary["avg_frequency"].round(2)
    summary["avg_monetary"] = summary["avg_monetary"].map(lambda x: f"${x:,.2f}")
    summary["revenue"] = summary["revenue"].map(lambda x: f"${x:,.2f}")
    st.dataframe(summary, width="stretch")

# -----------------------------
# TAB 2: COHORT RETENTION HEATMAP (Point 1)
# -----------------------------
with tab2:
    st.subheader("🗓️ Monthly Customer Retention Cohorts")
    st.write("Tracks how many customers from an initial cohort come back to purchase in subsequent months.")

    # Calculate Cohorts
    tx = transactions.copy()
    tx["order_month"] = tx["transaction_date"].dt.to_period("M")
    tx["cohort_month"] = tx.groupby("customer_id")["transaction_date"].transform("min").dt.to_period("M")

    cohort_data = tx.groupby(["cohort_month", "order_month"])["customer_id"].nunique().reset_index()
    cohort_data["cohort_index"] = (
        (cohort_data["order_month"].dt.year - cohort_data["cohort_month"].dt.year) * 12 +
        (cohort_data["order_month"].dt.month - cohort_data["cohort_month"].dt.month)
    )

    cohort_pivot = cohort_data.pivot(index="cohort_month", columns="cohort_index", values="customer_id")
    cohort_size = cohort_pivot.iloc[:, 0]
    retention_matrix = cohort_pivot.divide(cohort_size, axis=0) * 100

    fig_cohort, ax_cohort = plt.subplots(figsize=(10, 5))
    fig_cohort.patch.set_facecolor("#0e1117")
    ax_cohort.set_facecolor("#0e1117")

    sns.heatmap(
        retention_matrix, 
        annot=True, 
        fmt=".1f", 
        cmap="Blues", 
        cbar_kws={'label': 'Retention Rate (%)'},
        linewidths=0.5,
        ax=ax_cohort
    )
    ax_cohort.set_title("Retention Rate by Cohort Month (%)", fontsize=12, pad=10, color="white")
    ax_cohort.set_xlabel("Cohort Period (Months Later)", color="white")
    ax_cohort.set_ylabel("First Purchase Cohort", color="white")
    plt.xticks(color="white")
    plt.yticks(color="white")

    st.pyplot(fig_cohort)
    plt.close()

# -----------------------------
# TAB 3: CUSTOMER LIFETIME VALUE (CLV) PREDICTION (Point 2)
# -----------------------------
with tab3:
    st.subheader("💰 Customer Lifetime Value (CLV) Estimates")
    st.markdown("""
    **CLV Model**: $CLV = \\text{Average Order Value} \\times \\text{Purchase Frequency} \\times \\text{Assumed Lifespan}$
    """)

    lifespan_months = st.slider("Assumed Customer Lifespan (Months):", min_value=3, max_value=36, value=12)

    clv_df = rfm.copy()
    clv_df["aov"] = clv_df["monetary"] / clv_df["frequency"]
    
    # Monthly purchase velocity approximation
    time_span_days = (transactions["transaction_date"].max() - transactions["transaction_date"].min()).days
    monthly_frequency = clv_df["frequency"] / max(time_span_days / 30, 1)
    
    clv_df["predicted_clv"] = clv_df["aov"] * monthly_frequency * lifespan_months
    
    # Merge with segments
    clv_df = clv_df.merge(segments[["customer_id", "segment"]], on="customer_id", how="left")

    col_a, col_b = st.columns(2)
    col_a.metric("Avg Predicted CLV", f"${clv_df['predicted_clv'].mean():,.2f}")
    col_b.metric("Top 10% Customer CLV Threshold", f"${clv_df['predicted_clv'].quantile(0.90):,.2f}")

    st.subheader("High-Value Future Customers")
    display_clv = clv_df.sort_values("predicted_clv", ascending=False).head(20)[
        ["customer_id", "segment", "frequency", "monetary", "aov", "predicted_clv"]
    ]
    display_clv["monetary"] = display_clv["monetary"].map(lambda x: f"${x:,.2f}")
    display_clv["aov"] = display_clv["aov"].map(lambda x: f"${x:,.2f}")
    display_clv["predicted_clv"] = display_clv["predicted_clv"].map(lambda x: f"${x:,.2f}")

    st.dataframe(display_clv, width="stretch")

# -----------------------------
# TAB 4: BUSINESS PLAYBOOK (Point 3)
# -----------------------------
with tab4:
    st.subheader("🎯 Segment-Specific Marketing Actions")
    strategies = {
        "Champions": {
            "desc": "High spenders who buy very frequently and purchased recently.",
            "action": "Reward them with VIP access, early product drops, and referral incentives. No heavy discounts needed."
        },
        "Loyal Customers": {
            "desc": "Steady buyers with strong brand affinity and consistent basket size.",
            "action": "Upsell higher-tier products, offer cross-category bundles to increase basket size."
        },
        "Recent Customers": {
            "desc": "Bought recently for the first time or with low purchase frequency.",
            "action": "Send onboarding email drips, how-to guides, and a time-limited 10% coupon on second purchase."
        },
        "At Risk": {
            "desc": "Used to purchase frequently but have not engaged recently.",
            "action": "Trigger automated win-back emails, personalized 'We miss you' offers, and feedback surveys."
        },
        "Lost Customers": {
            "desc": "Lowest recency and frequency. Inactive for an extended period.",
            "action": "Aggressive clearance campaigns. Suppress from paid ads if unresponsive to save budget."
        }
    }

    for seg, data in strategies.items():
        with st.expander(f"📌 {seg} Strategy Guide"):
            st.markdown(f"**Customer Profile:** {data['desc']}")
            st.markdown(f"**Recommended Action:** {data['action']}")

    st.markdown("---")
    st.subheader("📥 Export Target Campaign Audience")
    sel_seg = st.selectbox("Choose Segment to Export:", list(strategies.keys()))
    export_df = segments[segments["segment"] == sel_seg][["customer_id", "recency", "frequency", "monetary"]]
    st.write(f"Target count: **{len(export_df):,}** customers ready for targeted outreach.")
    st.download_button(
        label=f"Download {sel_seg} Cohort CSV",
        data=export_df.to_csv(index=False).encode("utf-8"),
        file_name=f"{sel_seg.lower().replace(' ', '_')}_audience.csv",
        mime="text/csv"
    )

# -----------------------------
# TAB 5: CUSTOMER LOOKUP
# -----------------------------
with tab5:
    st.subheader("Search Customer Profile")
    cust_id = st.text_input("Enter Customer ID:")
    
    if cust_id:
        cust_row = rfm[rfm["customer_id"] == cust_id.strip()]
        if cust_row.empty:
            st.warning("Customer ID not found!")
        else:
            cust_row = cust_row.iloc[0]
            seg_match = segments[segments["customer_id"] == cust_id.strip()]
            seg_name = seg_match["segment"].iloc[0] if not seg_match.empty else "N/A"

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Segment", seg_name)
            m2.metric("Recency", f"{int(cust_row['recency'])} days")
            m3.metric("Frequency", f"{int(cust_row['frequency'])} orders")
            m4.metric("Monetary Spend", f"${cust_row['monetary']:,.2f}")

            st.write("**Customer Purchase History:**")
            history = (
                filtered_trans[filtered_trans["customer_id"] == cust_id.strip()]
                .groupby(["transaction_id", "transaction_date"])
                .agg(units=("quantity", "sum"), revenue=("item_revenue", "sum"))
                .reset_index()
                .sort_values("transaction_date", ascending=False)
            )
            history["revenue"] = history["revenue"].map(lambda x: f"${x:,.2f}")
            st.dataframe(history, width="stretch")