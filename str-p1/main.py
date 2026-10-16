import subprocess
import sys
import importlib
from pathlib import Path

import analytics_tool
import visualization_tool


# ============================================================
# E-COMMERCE CUSTOMER ANALYTICS SYSTEM
# ============================================================

BASE_DIR = Path(__file__).resolve().parent


# ============================================================
# RUN SCRIPT
# ============================================================

def run_script(script_name):

    script_path = BASE_DIR / script_name

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=BASE_DIR
    )

    return result.returncode == 0


# ============================================================
# REFRESH DATA
# ============================================================

def refresh_data():

    print("\n" + "=" * 60)
    print("              REFRESHING DATA")
    print("=" * 60)

    print("\n[1/2] Fetching data from BigQuery...")

    if not run_script("final_extract.py"):
        print("\nBigQuery data extraction failed.")
        return

    print("\nData extraction completed.")

    print("\n[2/2] Calculating RFM and customer segments...")

    if not run_script("rfm_analysis.py"):
        print("\nRFM analysis failed.")
        return

    print("\nRFM analysis completed.")
    print("Customer segmentation completed.")

    # Reload data after refresh
    importlib.reload(analytics_tool)
    importlib.reload(visualization_tool)

    print("\n" + "=" * 60)
    print("             DATA REFRESHED")
    print("=" * 60)


# ============================================================
# MAIN MENU
# ============================================================

def main():

    while True:

        print("\n" + "=" * 60)
        print("       E-COMMERCE CUSTOMER ANALYTICS SYSTEM")
        print("=" * 60)

        print("\n1. Customer Analysis")
        print("2. Sales Analysis")
        print("3. Customer Segmentation")
        print("4. Visualizations")
        print("5. Refresh Data")
        print("0. Exit")

        choice = input("\nChoose an option: ").strip()

        # ----------------------------------------------------
        # CUSTOMER ANALYSIS
        # ----------------------------------------------------

        if choice == "1":

            analytics_tool.customer_menu()

        # ----------------------------------------------------
        # SALES ANALYSIS
        # ----------------------------------------------------

        elif choice == "2":

            analytics_tool.sales_menu()

        # ----------------------------------------------------
        # CUSTOMER SEGMENTATION
        # ----------------------------------------------------

        elif choice == "3":

            analytics_tool.segmentation_menu()

        # ----------------------------------------------------
        # VISUALIZATIONS
        # ----------------------------------------------------

        elif choice == "4":

            visualization_tool.main()

        # ----------------------------------------------------
        # REFRESH DATA
        # ----------------------------------------------------

        elif choice == "5":

            refresh_data()

        # ----------------------------------------------------
        # EXIT
        # ----------------------------------------------------

        elif choice == "0":

            print("\n" + "=" * 60)
            print("Thank you for using the E-Commerce")
            print("Customer Analytics System.")
            print("=" * 60)

            break

        else:

            print("\nInvalid choice. Please try again.")


# ============================================================
# START PROGRAM
# ============================================================

if __name__ == "__main__":
    main()