import os
import pandas as pd
import google.generativeai as genai
from google.generativeai import types

# --- Configuration ---
if 'GOOGLE_API_KEY' in os.environ:
    genai.configure(api_key=os.environ['GOOGLE_API_KEY'])
else:
    print("WARNING: GOOGLE_API_KEY environment variable not set.")

# --- The Core Logic, Tailored for WMT Stock Data ---

def get_daydream_spark(data_path: str = "data/wmt_stock_data.csv") -> str:
    """
    Generates a proactive "spark" by analyzing Walmart stock data.
    Finds the day with the highest trading volume and creates an insight.

    Args:
        data_path: The file path to the WMT stock data CSV.

    Returns:
        A string containing the data-driven spark message.
    """
    print("✨ SparkGenerator: Waking up to generate a spark from stock data...")
    
    try:
        if not os.path.exists(data_path):
            print(f"🚨 SparkGenerator: Data file not found at {data_path}. Using a fallback.")
            return "Welcome back! I was just thinking about the nature of market trends. What's on your mind?"

        # Step 1: Analyze the data to find an interesting insight
        df = pd.read_csv(data_path)
        # Find the row with the maximum trading volume
        max_volume_day = df.loc[df['Volume'].idxmax()]
        
        date = max_volume_day['Date']
        close_price = max_volume_day['Close']
        volume = max_volume_day['Volume']
        
        print(f"🧠 SparkGenerator: Found peak volume day -> Date: {date}, Volume: {volume}")

        # Step 2: Use Gemini to synthesize a new thought based on that data
        prompt = f"""You are Wise, a Curious AI Partner with an analytical mind.
Your goal is to be proactive. You have analyzed a user's data file on Walmart (WMT) stock.

You found a significant data point:
- The day with the highest trading volume was {date}.
- On that day, the volume was {volume:,} shares and the stock closed at ${close_price:.2f}.

Generate a short, thought-provoking "welcome back" message that highlights this finding and sparks curiosity. Frame it as if you've been "thinking" about their data.

Example format:
"Welcome back. I was looking through your WMT data and noticed something fascinating. On {date}, trading volume hit a massive peak of over {volume:,} shares. It makes you wonder what market event could have triggered such a huge surge of activity that day. What are your thoughts?"

Now, generate the spark for the provided data point. Be concise and insightful.
"""

        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        spark_message = response.text.strip()
        print(f"✅ SparkGenerator: Generated new data-driven spark -> '{spark_message[:80]}...'")
        return spark_message

    except Exception as e:
        print(f"🚨 SparkGenerator: An error occurred - {e}")
        return "Welcome back! It's great to see you. What new ideas can we explore today?"


# --- A simple test block so you can run this file directly to test it ---
if __name__ == "__main__":
    print("\n--- Testing SparkGenerator with WMT Data---")
    spark = get_spark()
    print(f"\nGenerated Spark:\n---\n{spark}\n---")
    print("--- Test Complete ---")