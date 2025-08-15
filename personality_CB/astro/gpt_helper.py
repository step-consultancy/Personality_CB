import os
from dotenv import load_dotenv
import openai  # ✅ Updated for OpenAI v0.28

# Load environment variables from .env file
load_dotenv()

# --- CHANGE 1: Get the OpenAI API Key ---
openai_api_key = os.getenv("OPENAI_API_KEY")

# --- CHANGE 2: Set API Key globally (no client object in v0.28) ---
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file or environment variables.")

openai.api_key = openai_api_key

def get_openai_astrology(prompt: str) -> str:
    """
    Gets a response from the OpenAI API for a given prompt.
    """
    try:
        # --- CHANGE 3: API call using v0.28 syntax ---
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Or "gpt-3.5-turbo" if you prefer
            messages=[
                {"role": "system", "content": "You are a helpful and insightful astrologer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        # --- CHANGE 4: Access response with dict-style access ---
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error: {str(e)}"

# Example usage
if __name__ == "__main__":
    user_prompt = "Give me a horoscope for a Gemini for today, focusing on career."
    astrology_reading = get_openai_astrology(user_prompt)
    print("--- Your OpenAI Astrology Reading ---")
    print(astrology_reading)
