# 🝍 E-Commerce Customer Analytics & Segmentation Platform

An end-to-end data analytics and behavioral customer segmentation platform built with Python, Streamlit, and Google Cloud BigQuery. The system ingests e-commerce transaction data, calculates dynamic RFM scoring, models Customer Lifetime Value (CLV), computes cohort retention matrices, and exposes an executive decision-making dashboard.

## 🚧 Key Features
- **ELT Pipeline**: Extracts and processes granular transaction records from Google Cloud BigQuery.
- **RFM Segmentation Engine**: Recency, Frequency, and Monetary scoring that segments buyers into behavioral cohorts (*Champions*, *Loyal*, *At Risk*, *Lost*).
- **Cohort Retention Heatmap**: Tracks month-on-month customer retention curves using Seaborn matrix visualizations.
- **Predictive CLV Modeling**: Estimates projected customer lifetime spend using order velocity and basket metrics.
- **Executive Strategy Playbook**: Generates actionable markiting playbooks tailored per segment, complete with targeted CSV audience exports.
- **Customer 360° Lookup**: Searchable customer profile tool displaying individual purchase timelines and lifetime spending.

## 🛥️ Tech Stack
- **Languages**: Python
- **Cloud & Data Processing**: Google Cloud BigQuery, Pandas, NumPy
- **Visualizations & Interface**: Streamlit, Matplotlib, Seaborn
- **Security**: Python-dotenv (.env configuration)

## 🚀 Local Setup & Installation

1. **Clone repository:**
   ```bash
   git clone https://github.com/manikett/-2-ecommerce-customer-analytics.git
   cd -2-ecommerce-customer-analytics
   ```

2. **Set up virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Create a  `.env` file in the root directory:
   ```bash
   BIGQUERY_PROJECT_ID=your_gcp_project_id
   ```

5. **Run the Application:**
   ```bash
   # Run pipeline to generate datasets
   python run_project.py

   # Launch Streamlit dashboard
   python -m streamlit run app.py
   ```
