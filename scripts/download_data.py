"""
Download the Credit Card Fraud Detection dataset from Kaggle.

Prerequisites:
1. Create a Kaggle account at kaggle.com
2. Go to Account → API → Create New Token → downloads kaggle.json
3. Place kaggle.json at:
   - Mac/Linux: ~/.kaggle/kaggle.json
   - Windows: C:\\Users\\<username>\\.kaggle\\kaggle.json
4. Run: python scripts/download_data.py
"""

import os
import subprocess
import sys

DATASET = "mlg-ulb/creditcardfraud"
OUTPUT_DIR = "data/raw"


def main():
    # Check kaggle is installed
    try:
        import kaggle
    except ImportError:
        print("Installing kaggle...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "kaggle"])
        import kaggle

    # Check credentials exist
    kaggle_dir = os.path.expanduser("~/.kaggle")
    kaggle_json = os.path.join(kaggle_dir, "kaggle.json")
    if not os.path.exists(kaggle_json):
        print(f"""
❌ kaggle.json not found at {kaggle_json}

To fix:
1. Go to https://www.kaggle.com/settings
2. Scroll to API section → Create New Token
3. Move the downloaded kaggle.json to {kaggle_dir}/kaggle.json
4. Run: chmod 600 {kaggle_dir}/kaggle.json  (Mac/Linux only)
        """)
        sys.exit(1)

    # Download
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Downloading {DATASET} to {OUTPUT_DIR}...")

    from kaggle.api.kaggle_api_extended import KaggleApiExtended
    api = KaggleApiExtended()
    api.authenticate()
    api.dataset_download_files(DATASET, path=OUTPUT_DIR, unzip=True)

    csv_path = os.path.join(OUTPUT_DIR, "creditcard.csv")
    if os.path.exists(csv_path):
        import pandas as pd
        df = pd.read_csv(csv_path)
        print(f"""
✅ Dataset downloaded successfully
   Path: {csv_path}
   Rows: {len(df):,}
   Fraud cases: {df['Class'].sum():,} ({df['Class'].mean()*100:.3f}%)
   Columns: {list(df.columns)}

Next step: python src/model/train.py
        """)
    else:
        print(f"⚠️  Download complete but {csv_path} not found — check {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
