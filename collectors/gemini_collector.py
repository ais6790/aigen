# gemini_collector.py
import os
import random
import time
import json
from datetime import datetime

try:
    import google.generativeai as genai
except ImportError:
    os.system("pip install -q google-generativeai")
    import google.generativeai as genai

# CONFIG
API_KEYS = {
    "key1": "AIzaSyC_meFvwj7O-r_vH-s9OaM8VnLGUFY1478",
    "key2": "AIzaSyDxO8BQjC_z4rS2V6tI5iyHAF-pAFzIj14"
}
MODEL_NAME = "gemini-1.5-pro"
TEMPERATURE = 0.8
MAX_RETRIES = 3
RETRY_SLEEP = 2
SAVE_BASE = "/content/drive/MyDrive/aigen/daily_dumps"

# Set the Gemini API key from config

def set_api_key(key_name):
    genai.configure(api_key=API_KEYS[key_name])

# Generate varied prompts dynamically

def generate_self_prompt():
    topics = [
        "AI ethics", "data structures", "algorithms", "startups",
        "psychology", "philosophy", "economics", "education",
        "technology", "machine learning", "deep learning", "code debugging",
        "creative writing", "social scenarios", "history", "law", "medicine"
    ]
    topic = random.choice(topics)
    style = random.choice([
        "Generate a thoughtful question about",
        "Create a challenging question in the domain of",
        "Write a deep question and answer about",
        "Pose a creative question on",
        "Formulate an advanced prompt based on"
    ])
    return f"{style} {topic}. Provide a detailed answer."

# Generate content from Gemini

def fetch_qa(prompt, retries=MAX_RETRIES):
    for _ in range(retries):
        try:
            model = genai.GenerativeModel(MODEL_NAME)
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(RETRY_SLEEP)
    return None

# Parse Q&A format from Gemini output

def split_qa(text):
    if "Answer:" in text:
        parts = text.split("Answer:", 1)
        return {
            "question": parts[0].replace("Question:", "").strip(),
            "answer": parts[1].strip()
        }
    elif "Q:" in text and "A:" in text:
        parts = text.split("A:", 1)
        return {
            "question": parts[0].replace("Q:", "").strip(),
            "answer": parts[1].strip()
        }
    return None

# Collect and deduplicate QA pairs

def collect(key_name, count=1000):
    print(f"\n🚀 Collecting {count} QA pairs using {key_name}...")
    set_api_key(key_name)
    qa_pairs = []
    seen_questions = set()

    for i in range(count):
        prompt = generate_self_prompt()
        output = fetch_qa(prompt)
        if output:
            qa = split_qa(output)
            if qa and qa['question'] not in seen_questions:
                qa_pairs.append(qa)
                seen_questions.add(qa['question'])
                print(f"✅ {i+1}/{count}: {qa['question'][:60]}...")
            else:
                print("⚠️ Duplicate or unrecognized format")
        else:
            print("❌ No output")
    return qa_pairs

# Save to a daily file per key

def save_dataset(data, key_name):
    date_str = datetime.now().strftime("%Y-%m-%d")
    out_path = os.path.join(SAVE_BASE, key_name, f"{date_str}.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Saved {len(data)} QA pairs to {out_path}")
