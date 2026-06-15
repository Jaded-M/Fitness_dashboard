import google.generativeai as genai
import os
import re

def load_api_key():
    key_path = "G API key.txt"
    try:
        with open(key_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            match = re.search(r"AIza[0-9A-Za-z-_]{35,}", content)
            if match:
                return match.group(0)
    except Exception as e:
        print(f"Error reading key: {e}")
    return None

key = load_api_key()
if not key:
    print("No API key found in G API key.txt")
else:
    try:
        genai.configure(api_key=key)
        print("Available models:")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
    except Exception as e:
        print(f"Error listing models: {e}")
