import os
import json
import random
import time
from datetime import datetime

# Optional: For Google Colab Drive mounting
try:
    import google.colab
    from google.colab import drive
    drive.mount('/content/drive')
    SAVE_PATH = "/content/drive/MyDrive/aigen/daily_dumps"
    print("✅ Running in Colab, Drive mounted.")
except ImportError:
    SAVE_PATH = "./daily_dumps"
    print("⚠️ Not in Colab, saving locally.")

# Install/Import Google Gemini SDK
try:
    import google.generativeai as genai
except ImportError:
    print("Installing google-generativeai...")
    os.system("pip install --upgrade google-generativeai")
    import google.generativeai as genai

# Rotate multiple API keys
API_KEYS = [
    "AIzaSyBmCTbbAZLWB30sJBpo5PrXCEVWFaBpzcA",
    "AIzaSyDxO8BQjC_z4rS2V6tI5iyHAF-pAFzIj14"
]
genai.configure(api_key=random.choice(API_KEYS))

# Use updated Gemini model
MODEL_NAME = "models/gemini-1.5-pro"

# Generate diverse prompts
def generate_prompt():
    level = random.choice(["easy", "medium", "hard", "tricky", "technical", "creative"])
    topic = random.choice([
        "AI", "Machine Learning", "Ethics", "Philosophy", "Mathematics", "Programming",
        "Data Structures", "Startups", "History", "Space", "Cybersecurity", "Logic", "Python"
    ])
    return f"Give a {level} question and answer on {topic} suitable for training an AI model. Format like:\nQuestion: ...\nAnswer: ..."

# Extract Q/A from text
def parse_response(text):
    try:
        lines = text.strip().splitlines()
        q = next((l for l in lines if l.lower().startswith("question:")), None)
        a = next((l for l in lines if l.lower().startswith("answer:")), None)
        if q and a:
            return {
                "question": q[len("Question:"):].strip(),
                "answer": a[len("Answer:"):].strip()
            }
    except Exception as e:
        print("❌ Parse error:", e)
    return None

# Call Gemini API
def fetch_qa(prompt, retries=3):
    for _ in range(retries):
        try:
            model = genai.GenerativeModel(MODEL_NAME)
            response = model.generate_content(prompt)
            if response and response.text:
                return parse_response(response.text)
        except Exception as e:
            print("⚠️ Error:", e)
            time.sleep(2)
    return None

# Collect dataset
def collect(n=1000):
    dataset = []
    for i in range(n):
        prompt = generate_prompt()
        qa = fetch_qa(prompt)
        if qa:
            dataset.append(qa)
            print(f"✅ {i+1}/{n} collected")
        else:
            print(f"❌ Failed {i+1}/{n}")
        time.sleep(random.uniform(1.1, 1.9))
    return dataset

# Save to file
def save_dataset(data):
    if not data:
        print("⚠️ Nothing to save.")
        return
    os.makedirs(SAVE_PATH, exist_ok=True)
    fname = datetime.now().strftime("%Y-%m-%d") + ".json"
    fpath = os.path.join(SAVE_PATH, fname)
    try:
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"📁 Saved {len(data)} Q&A pairs to {fpath}")
    except Exception as e:
        print(f"❌ Save failed: {e}")

# Main runner
if __name__ == "__main__":
    data = collect(1000)
    save_dataset(data)
