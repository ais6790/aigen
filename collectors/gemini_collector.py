import os
import json
import time
import random
from datetime import datetime
import google.generativeai as genai
from google.colab import drive

# Mount Google Drive
drive.mount('/content/drive')

# Choose an API key (you can rotate)
API_KEYS = [
    "AIzaSyBmCTbbAZLWB30sJBpo5PrXCEVWFaBpzcA",
    "AIzaSyDxO8BQjC_z4rS2V6tI5iyHAF-pAFzIj14"
]
genai.configure(api_key=random.choice(API_KEYS))

model = genai.GenerativeModel("gemini-pro")
SAVE_PATH = "/content/drive/MyDrive/aigen/daily_dumps"

meta_prompt = """
Generate one unique, high-quality question and its answer for fine-tuning a large language model. The question should be challenging, educational, or thought-provoking. Avoid trivia or generic topics. Output format:

Question: <your question here>
Answer: <detailed answer here>
"""

def parse_qa(raw_text):
    try:
        lines = raw_text.strip().splitlines()
        q = next((line for line in lines if line.lower().startswith("question:")), None)
        a = next((line for line in lines if line.lower().startswith("answer:")), None)
        if q and a:
            return {
                "question": q[len("Question:"):].strip(),
                "answer": a[len("Answer:"):].strip()
            }
    except:
        return None
    return None

def generate_qa(retries=3):
    for _ in range(retries):
        try:
            response = model.generate_content(meta_prompt)
            parsed = parse_qa(response.text)
            if parsed:
                return parsed
        except Exception as e:
            print("Error generating QA:", e)
            time.sleep(2)
    return None

def collect_dataset(n=1000):
    data = []
    for i in range(n):
        qa = generate_qa()
        if qa:
            data.append(qa)
            print(f"✅ {i+1}/{n}: {qa['question']}")
        else:
            print(f"❌ Skipped at {i+1}")
        time.sleep(1)  # avoid rate limit
    return data

def save_data(data):
    os.makedirs(SAVE_PATH, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    file_path = os.path.join(SAVE_PATH, f"{date_str}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(data)} Q&A pairs to {file_path}")

if __name__ == "__main__":
    dataset = collect_dataset(1000)
    save_data(dataset)
