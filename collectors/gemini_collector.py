import os
import json
import random
import time
from datetime import datetime
import google.generativeai as genai
from google.colab import drive

# Mount Google Drive
drive.mount('/content/drive')

# API keys (rotated randomly)
API_KEYS = [
    "AIzaSyBmCTbbAZLWB30sJBpo5PrXCEVWFaBpzcA",
    "AIzaSyDxO8BQjC_z4rS2V6tI5iyHAF-pAFzIj14"
]
genai.configure(api_key=random.choice(API_KEYS))
model = genai.GenerativeModel("gemini-pro")

# Google Drive save path
SAVE_PATH = "/content/drive/MyDrive/aigen/daily_dumps"

# Dynamic meta-prompts for variety
def generate_dynamic_prompt():
    difficulty = random.choice(["easy", "medium", "hard", "technical", "creative"])
    topic = random.choice([
        "AI", "Physics", "History", "Programming", "Mathematics",
        "Philosophy", "Economics", "Logic", "Ethics", "Psychology"
    ])
    return f"Give me a {difficulty} level question and answer about {topic} suitable for training an AI model."

# Parse Gemini response into {"question": ..., "answer": ...}
def parse_qa(raw_text):
    try:
        lines = raw_text.strip().splitlines()
        q_line = next((line for line in lines if line.lower().startswith("question:")), "")
        a_line = next((line for line in lines if line.lower().startswith("answer:")), "")
        question = q_line[len("Question:"):].strip()
        answer = a_line[len("Answer:"):].strip()
        if question and answer:
            return {"question": question, "answer": answer}
    except Exception as e:
        print("❌ Parse error:", e)
    return None

# Query Gemini with retries
def generate_qa(prompt, retries=3):
    for _ in range(retries):
        try:
            response = model.generate_content(prompt)
            parsed = parse_qa(response.text)
            if parsed:
                return parsed
        except Exception as e:
            print(f"Retrying for prompt: {prompt} - Error: {e}")
            time.sleep(2)
    return None

# Collect dataset
def collect_dataset(n=1000):
    data = []
    for i in range(n):
        prompt = generate_dynamic_prompt()
        qa = generate_qa(prompt)
        if qa:
            data.append(qa)
            print(f"✅ Collected {len(data)}/{n}")
        else:
            print(f"⚠️ Failed to collect for prompt {i+1}")
        time.sleep(random.uniform(1.2, 2.0))  # Avoid rate limits
    return data

# Save data as JSON to Google Drive
def save_data(data):
    if not data:
        print("⚠️ No data to save. Skipping file write.")
        return
    os.makedirs(SAVE_PATH, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    file_path = os.path.join(SAVE_PATH, f"{date_str}.json")
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved {len(data)} Q&A pairs to {file_path}")
    except Exception as e:
        print(f"❌ Failed to save JSON: {e}")

# Entry point
if __name__ == "__main__":
    try:
        dataset = collect_dataset(1000)
        print("🧪 Preview of first 2:", dataset[:2])
        save_data(dataset)
    except Exception as e:
        print("❌ Script failed:", e)
