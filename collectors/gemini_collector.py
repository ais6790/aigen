import os
import time
import json
from google.colab import drive
from datetime import datetime
from tqdm import tqdm
import google.generativeai as genai
import google.api_core.exceptions as gexc

# ✅ Mount Google Drive
if not os.path.exists('/content/drive'):
    print("⛔ Drive not available, make sure you're in Colab.")
else:
    drive.mount('/content/drive')
    print("✅ Google Drive mounted.")

# 🔑 Your API keys
API_KEYS = [
    "AIzaSyC_meFvwj7O-r_vH-s9OaM8VnLGUFY1478"
]

# 📁 Output directory
output_dir = '/content/drive/MyDrive/aigen_collector_output'
os.makedirs(output_dir, exist_ok=True)

def try_with_key(api_key, prompt):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(prompt)
        return response.text.strip()
    except gexc.ResourceExhausted as e:
        print(f"❌ Quota exceeded for key: {api_key}")
        raise e
    except Exception as e:
        print(f"⚠️ Error with key {api_key}: {e}")
        raise e

def collect(n=10, delay=2):
    results = []
    current_key_index = 0
    total_keys = len(API_KEYS)

    for i in tqdm(range(n), desc="🔄 Collecting"):
        prompt = f"Generate a short creative writing prompt {i + 1}"
        success = False

        for attempt in range(total_keys):
            key = API_KEYS[current_key_index]
            try:
                text = try_with_key(key, prompt)
                results.append({'id': i + 1, 'prompt': prompt, 'response': text})
                success = True
                break
            except gexc.ResourceExhausted:
                current_key_index = (current_key_index + 1) % total_keys
                time.sleep(1)
            except Exception as e:
                print(f"❌ Unhandled error: {e}")
                break

        if not success:
            results.append({'id': i + 1, 'prompt': prompt, 'response': None, 'error': 'All keys failed'})
        time.sleep(delay)

    return results

# ✅ Start collecting
data = collect(n=10, delay=2)

# ✅ Save to Drive
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output_path = os.path.join(output_dir, f'gemini_collected_{timestamp}.json')
with open(output_path, 'w') as f:
    json.dump(data, f, indent=2)

print(f"\n✅ Saved {len(data)} items to:\n{output_path}")
