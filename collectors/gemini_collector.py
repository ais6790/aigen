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

API_KEYS = {
    "key1": "AIzaSyC_meFvwj7O-r_vH-s9OaM8VnLGUFY1478",
    "key2": "AIzaSyAznXRjbXnLDrvdzyXyhwIUeKJdSSnoLlI"
}

MODEL_NAME = "gemini-1.5-pro"
TEMPERATURE = 0.8
PROMPT_STYLE = """Generate a unique question and answer pair in any meaningful domain: technology, science, AI ethics, creativity, education, etc.
Format it as:
Question: ...
Answer: ...
"""

DAILY_COUNT = 1000
LOCAL_BASE = "/home/ais/aigen_dumps"
RCLONE_REMOTE = "gdrive"
RCLONE_FOLDER = "aigen/daily_dumps"

def set_key(source: str):
    genai.configure(api_key=API_KEYS[source])

def fetch_qa(prompt: str) -> dict | None:
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

def collect(source: str, total: int = DAILY_COUNT):
    set_key(source)
    collected = []
    seen_questions = set()
    print(f"🚀 Collecting {total} QA pairs using {source}...")

    while len(collected) < total:
        qa = fetch_qa(PROMPT_STYLE)
        if qa and qa["question"] not in seen_questions:
            collected.append(qa)
            seen_questions.add(qa["question"])
            print(f"✅ {len(collected)}/{total}: {qa['question'][:60]}")
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
