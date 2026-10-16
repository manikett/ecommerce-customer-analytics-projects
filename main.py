"""
Unified E-Commerce Customer Analytics & Visualization Pipeline
"""
import sys
import os

# Add src folder to system path so modules can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

def main():
    print("🚀 Starting Unified E-Commerce Customer Analytics Pipeline...")
    
    # 1. Data Analysis / RFM Module Run Karein
    print("\n--- Step 1: Running Data Analysis & RFM Module ---")
    try:
        import rfm_analysis
        print("✅ RFM Analysis completed successfully.")
    except Exception as e:
        print(f"⚠️ Note on RFM analysis: {e}")

    # 2. Visualization Module Run Karein
    print("\n--- Step 2: Generating Visualizations ---")
    try:
        import visualization_tool
        print("✅ Visualizations generated successfully.")
    except Exception as e:
        print(f"⚠️ Note on visualization: {e}")

    print("\n🎉 Pipeline execution finished! Check the 'outputs/' folder for results.")

if __name__ == "__main__":
    main()
