# scripts/process_dataset.py

import pandas as pd
import os

print("Starting dataset processing for Wise...")

# --- A more robust way to define file paths ---
# This locates the script's own directory first.
script_dir = os.path.dirname(__file__) 

# Now, we build paths relative to the script's location.
# This makes the script work no matter where you run it from.
# os.path.join handles the slashes correctly for any OS.
raw_data_path = os.path.join(script_dir, '..', 'data', 'data', 'WMT_1970-10-01_2025-01-31.csv')
output_path = os.path.join(script_dir, '..', 'app', 'data', 'wmt_stock_data.csv')

# Use os.path.abspath to show the full, unambiguous path for debugging
print(f"Attempting to read raw data from absolute path: {os.path.abspath(raw_data_path)}")


try:
    # Check if the output directory exists, if not, create it
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    # Read the raw data
    df = pd.read_csv(raw_data_path)

    # --- Data Cleaning and Preparation ---
    df['Date'] = pd.to_datetime(df['Date'])
    df_recent = df[df['Date'] > '2020-01-01'].copy()
    df_recent['Year'] = df_recent['Date'].dt.year
    df_recent['Month'] = df_recent['Date'].dt.month
    df_recent.to_csv(output_path, index=False)

    print(f"\nProcessing complete!")
    print(f"Saved {len(df_recent)} recent stock records to: {os.path.abspath(output_path)}")

except FileNotFoundError:
    print(f"\nFATAL ERROR: The raw data file was not found.")
    print("Please double-check two things:")
    print("1. You have a folder named 'data' in your main 'wise-adk-hackathon' directory.")
    print("2. Inside that 'data' folder, the file 'WMT_1970-10-01_2025-01-31.csv' exists.")
    
except Exception as e:
    print(f"\nAn unexpected error occurred: {e}")