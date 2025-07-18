import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_URL = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
    "Content-Type": "application/json"
}

def generate_summary(parsed_text):
    prompt = (
        "You are a clinical AI assistant. You are given a lab report. "
        "For each test value:\n"
        "- Compare it to the reference range\n"
        "- Say if it is Normal / Low / Very Low / High\n"
        "- Explain abnormal values in simple, medically accurate terms\n"
        "- Provide a short summary of findings at the end.\n\n"
        f"Lab report:\n{parsed_text}"
    )

    payload = {
        "model": "mistralai/mixtral-8x7b-instruct",  # can switch to e.g. openai/gpt-4, meta-llama/70b-instruct, etc.
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 600
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"❌ Error: {e}\nResponse: {response.text if 'response' in locals() else ''}"
