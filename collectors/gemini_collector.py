import os
import random
import time
import json

# Install and import required packages
try:
    import google.generativeai as genai
except ImportError:
    os.system("pip install -q google-generativeai")
    import google.generativeai as genai

# Detect if running in Google Colab
try:
    from google.colab import drive
    IN_COLAB = True
except ImportError:
    IN_COLAB = False

# Mount Google Drive (for Colab)
if IN_COLAB:
    drive.mount('/content/drive', force_remount=True)
    print("✅ Running in Colab, Drive mounted.")

# Gemini API Configuration
API_KEYS = [
    "AIzaSyC_meFvwj7O-r_vH-s9OaM8VnLGUFY1478",
    "AIzaSyDxO8BQjC_z4rS2V6tI5iyHAF-pAFzIj14"
]

MODEL_NAME = "gemini-1.5-pro"
TEMPERATURE = 0.8
MAX_RETRIES = 3
RETRY_SLEEP = 2  # seconds between retries

PROMPT_POOL = [
    "Write a unique and insightful machine learning interview question and its detailed answer.",
    "Generate a high-quality startup founder case study question and model answer.",
    "Create a thoughtful ethical dilemma question related to artificial intelligence, with a sample answer.",
    "Give a complex real-world scenario that requires a creative algorithmic solution, along with the reasoning.",
    "Design a speculative yet grounded question about AI's future impact on society, and answer it."
]

def set_random_key():
    key = random.choice(API_KEYS)
    genai.configure(api_key=key)

def fetch_qa(prompt, retries=MAX_RETRIES):
    for attempt in range(retries):
        try:
            set_random_key()
            model = genai.GenerativeModel(MODEL_NAME)
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(RETRY_SLEEP)
    return None

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
    else:
        return None

def collect(n=10):
    qa_pairs = []
    for i in range(n):
        prompt = random.choice(PROMPT_POOL)
        print(f"\n🧠 Prompt {i+1}/{n}: {prompt}")
        output = fetch_qa(prompt)
        if output:
            qa = split_qa(output)
            if qa:
                qa_pairs.append(qa)
                print(f"✅ {i+1}/{n} collected")
            else:
                print("⚠️ Could not parse QA")
        else:
            print("❌ Failed to fetch content")
    return qa_pairs

def save_dataset(data, output_path="/content/drive/MyDrive/aigen/qa_dataset.json"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n📁 Saved {len(data)} QA pairs to {output_path}")
