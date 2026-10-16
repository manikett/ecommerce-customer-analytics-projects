import subprocess
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent

def run_script(script_name):
    print("\n" + "=" * 60)
    print(f"Running: {script_name}")
    print("=" * 60)

    script_path = BASE_DIR / script_name
    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=BASE_DIR
    )

    if result.returncode != 0:
        print(f"\nERROR: {script_name} failed.")
        sys.exit(1)

    print(f"\n{script_name} completed successfully.")

def check_file(file_path):
    path = BASE_DIR / file_path
    if path.exists():
        size_kb = path.stat().st_size / 1024
        print(f"✓ {file_path} updated ({size_kb:.1f} KB)")
    else:
        print(f"✗ {file_path} was not created.")
        sys.exit(1)

def main():
    print("\n" + "=" * 60)
    print("     E-COMMERCE ANALYTICS PROJECT REFRESH")
    print("=" * 60)
    print("\nRefresh started at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Step 1: BigQuery Extract
    run_script("final_extract.py")
    check_file("data/transactions.csv")

    # Step 2: RFM Calculation & Segmentation
    run_script("rfm_analysis.py")
    check_file("data/rfm.csv")
    check_file("data/customer_segments.csv")

    print("\n" + "=" * 60)
    print("        PROJECT REFRESH COMPLETED")
    print("=" * 60)
    print("\nUpdated files:")
    print("✓ data/transactions.csv")
    print("✓ data/rfm.csv")
    print("✓ data/customer_segments.csv")

    print("\nFinished at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("\nYou can now run:")
    print("  python main.py")

if __name__ == "__main__":
    main()