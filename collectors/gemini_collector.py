# gemini_collector.py (improved with prompt variation)

import os
import random
import time
import json
import subprocess

try:
    import google.generativeai as genai
except ImportError:
    os.system("pip install -q google-generativeai")
    import google.generativeai as genai

# --- Configuration ---
API_KEYS = {
    "key1": "AIzaSyC_meFvwj7O-r_vH-s9OaM8VnLGUFY1478",
    "key2": "AIzaSyDxO8BQjC_z4rS2V6tI5iyHAF-pAFzIj14"
}

MODEL_NAME = "gemini-1.5-pro"
LOCAL_BASE = "/home/ais/aigen_dumps"
RCLONE_REMOTE = "gdrive"
RCLONE_FOLDER = "aigen/daily_dumps"

# --- Prompt Generator ---
def generate_prompt():
    topics = [
        "artificial intelligence", "deep learning", "quantum computing",
        "AI ethics", "digital privacy", "psychology", "philosophy of mind",
        "startups", "education", "future of work", "space travel"
    ]

    templates = [
        "Pose a creative, difficult question about {topic} and provide a thoughtful answer.",
        "Imagine you're writing a thought experiment about {topic}. Give a question and answer.",
        "As a university professor of {topic}, create a question you'd ask on a final exam, and then answer it.",
        "Write a practical real-world scenario involving {topic}, then explain it in a Q&A format.",
        "Ask a controversial or speculative question about {topic}, and then answer it carefully.",
        "Write a historical Q&A where the topic is {topic}, but the style is conversational and philosophical."
    ]

    topic = random.choice(topics)
    template = random.choice(templates)
    return template.format(topic=topic)

# --- Core Functions ---
def set_key(source: str):
    genai.configure(api_key=API_KEYS[source])

def fetch_qa(prompt: str):
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        if response and response.text:
            return split_qa(response.text)
    except Exception as e:
        print(f"⚠️ Error: {e}")
    return None

def split_qa(text: str):
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

def collect(source: str, total: int = 1000):
    set_key(source)
    collected = []
    seen_questions = set()
    print(f"\n🚀 Collecting {total} QA pairs using {source}...")

    while len(collected) < total:
        prompt = generate_prompt()
        qa = fetch_qa(prompt)
        if qa and qa['question'] not in seen_questions:
            collected.append(qa)
            seen_questions.add(qa['question'])
            print(f"✅ {len(collected)}/{total}: {qa['question'][:60]}...")
        else:
            print("⚠️ Duplicate or unrecognized format")
        time.sleep(1)

    return collected

def save_dataset(data: list, source: str):
    today = time.strftime("%Y-%m-%d")
    folder = os.path.join(LOCAL_BASE, source)
    os.makedirs(folder, exist_ok=True)
    out_path = os.path.join(folder, f"{today}.json")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Saved {len(data)} QA pairs to {out_path}")
    sync_to_drive(source)

def sync_to_drive(source: str):
    local_path = os.path.join(LOCAL_BASE, source)
    remote_path = f"{RCLONE_REMOTE}:{RCLONE_FOLDER}/{source}"
    try:
        print(f"🔄 Syncing {local_path} → {remote_path}...")
        subprocess.run(["/home/ais/rclone", "copy", local_path, remote_path], check=True)
        print("✅ Synced successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Rclone sync failed: {e}")
