import os
import json
from dotenv import load_dotenv
import openai

# Load environment variables (API key)
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY is missing in .env")

openai.api_key = api_key

# First intro question
INTRO_QUESTION = "Hello! I'm a chatbot designed to understand your personality. To begin, please tell me a little about yourself."

# ✅ Generate dynamic multiple-choice questions after intro
def select_best_questions(user_intro):
    prompt = f"""
    Based on the following user intro: "{user_intro}", generate 25 personality assessment questions.
    For each question, include 4 multiple-choice options.

    Output ONLY a valid JSON array like this:
    [
      {{
        "question": "How do you handle stress?",
        "options": ["Stay calm", "Express emotions", "Isolate", "Distract myself"]
      }},
      ...
    ]
    
    Do NOT add any commentary or markdown (no ```json or explanation).
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-1106-preview",  # Can change to gpt-3.5-turbo for lower cost
            messages=[{"role": "system", "content": "You are a JSON-only response generator."},
                      {"role": "user", "content": prompt}],
            temperature=0.7
        )

        raw = response.choices[0].message["content"].strip()

        # If the response starts with markdown or other unexpected content, strip it
        if raw.startswith("```json") or raw.startswith("```"):
            raw = raw.strip("`").strip()
            raw = "\n".join(line for line in raw.splitlines() if not line.strip().startswith("json"))

        # Attempt to parse as JSON
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            # If JSON fails, print raw and fallback
            print("❌ OpenAI returned malformed JSON:\n\n" + raw)
            return []

    except Exception as e:
        print(f"Error occurred: {e}")
        # Fallback to default set of questions
        return [
            {"question": "What's one of your favorite hobbies?", "options": ["Reading", "Sports", "Gaming", "Crafting"]},
            {"question": "Are you more of an early bird or a night owl?", "options": ["Early bird", "Night owl", "Both", "Neither"]}
        ]

# ✅ Generate full personality profile
def generate_personality_profile(user_intro, qa_pairs):
    questions_formatted = "\n".join([f"{i+1}. Q: {q}\nA: {a}" for i, (q, a) in enumerate(qa_pairs)])

    prompt = f"""
    Based on the following introduction and answers, identify the user's dominant personality type in ONE WORD.
    Then, provide a short personality profile (3-4 sentences).
    Also list 2-3 strengths (Pros) and 2-3 limitations (Cons) of this personality type.

    Introduction: "{user_intro}"
    Answers:
    {questions_formatted}

    Format the response like this:

    Personality Type: <One Word>

    Pros:
    - <Positive trait 1>
    - <Positive trait 2>
    - <Optional positive trait 3>

    Cons:
    - <Limitation 1>
    - <Limitation 2>
    - <Optional limitation 3>

    Profile: <3-4 sentence paragraph>
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-1106-preview",
            messages=[{"role": "system", "content": "You are a personality analyst."},
                      {"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        print(f"Error generating personality profile: {e}")
        return "Unable to generate personality profile at this time."

# ✅ Friendly one-liner feedback
def generate_feedback(question, answer):
    prompt = f"""
    A user responded to a personality question.

    Q: {question}
    A: {answer}

    Write a short, friendly, empathetic, and informal 1-line response as a personality chatbot. Make it warm and encouraging.
    Example: "That's a great way to handle things!" or "Sounds like you’re someone who values honesty!"
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-1106-preview",
            messages=[{"role": "system", "content": "You are a warm and encouraging personality chatbot."},
                      {"role": "user", "content": prompt}],
            temperature=0.8
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        print(f"Error generating feedback: {e}")
        return "That sounds interesting!"

