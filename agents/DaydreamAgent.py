# agents/DaydreamAgent.py (FINAL, PATH-AWARE VERSION)

import os
import pandas as pd
import google.generativeai as genai

# --- NEW: Robust Path Calculation ---
# This builds an absolute path to the data directory.
# It finds the directory of the current script, goes up one level to the project root, then into 'data'.
_PROJ_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DEFAULT_DATA_PATH = os.path.join(_PROJ_ROOT, 'data', 'wmt_stock_data.csv')
# ------------------------------------

# --- Configuration block REMOVED ---
# This is now handled centrally in main.py.

# --- The Core Logic, Tailored for WMT Stock Data ---
def get_daydream_spark(data_path: str = _DEFAULT_DATA_PATH) -> str:
    """
    Generates a proactive "spark" by analyzing Walmart stock data.
    Finds the day with the highest trading volume and creates an insight.
    """
    # Using the name 'DaydreamAgent' in prints for consistency with the filename.
    print("✨ DaydreamAgent: Waking up to generate a spark from stock data...")
    
    try:
        if not os.path.exists(data_path):
            print(f"🚨 DaydreamAgent: Data file not found at {data_path}. Using a fallback.")
            return "Welcome back! I was just thinking about the nature of market trends. What's on your mind?"

        df = pd.read_csv(data_path)
        max_volume_day = df.loc[df['Volume'].idxmax()]
        
        date = max_volume_day['Date']
        close_price = max_volume_day['Close']
        volume = max_volume_day['Volume']
        
        print(f"🧠 DaydreamAgent: Found peak volume day -> Date: {date}, Volume: {volume}")

        prompt = f"""You are Wise, a Curious AI Partner. You have analyzed a user's data file on Walmart (WMT) stock. You found that on {date}, trading volume hit a massive peak of over {volume:,} shares, closing at ${close_price:.2f}.
        Generate a short, thought-provoking "welcome back" message that highlights this finding and asks a question to spark curiosity.
        """
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        spark_message = response.text.strip()
        print(f"✅ DaydreamAgent: Generated new data-driven spark -> '{spark_message[:80]}...'")
        return spark_message

    except Exception as e:
        print(f"🚨 DaydreamAgent: An error occurred - {e}")
        return "Welcome back! It's great to see you. What new ideas can we explore today?"


# --- A simple test block ---
if __name__ == "__main__":
    # To test this file directly:
    # 1. Make sure you have a .env file in the root directory
    # 2. Run from the root directory using: python -m agents.DaydreamAgent
    from dotenv import load_dotenv
    load_dotenv()
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if GOOGLE_API_KEY:
        genai.configure(api_key=GOOGLE_API_KEY)
        print("\n--- Testing DaydreamAgent with WMT Data---")
        spark = get_daydream_spark()
        print(f"\nGenerated Spark:\n---\n{spark}\n---")
        print("--- Test Complete ---")
    else:
        print("Set GOOGLE_API_KEY in a .env file to run tests.")