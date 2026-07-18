import re
import requests
import json

import os
API_KEY = os.getenv("GROQ_API_KEY")

MODEL = "llama-3.3-70b-versatile"

def extract_ips(text):
    return re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", text)

def extract_usernames(text):
    return re.findall(r"user\s+'?(\w+)'?", text, re.IGNORECASE)

def extract_timestamps(text):
    return re.findall(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", text)

def safe_parse_json(content):
    try:
        # Strip code fences if present
        if content.startswith("```"):
            # Remove leading/trailing backticks
            content = content.strip("`")
            # Remove 'json' keyword if present
            content = content.replace("json", "", 1).strip()
        return json.loads(content)
    except Exception as e:
        return {"error": f"Failed to parse JSON: {e}", "raw": content}

def analyze_logs(log_text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
    You are a cybersecurity analyst. Analyze the logs and return ONLY valid JSON.
    Do not include explanations, code fences, or text outside the JSON.
    {{
      "summary": "...",
      "severity_level": "Low/Medium/High/Critical",
      "severity_score": 1-10,
      "threat_types": ["..."],
      "suspicious_ips": ["..."],
      "ioc": ["..."],
      "recommended_actions": ["..."]
    }}

    Logs:
    {log_text}
    """

    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful AI security assistant."},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    result = response.json()

    # Defensive check in case API returns differently
    if "choices" in result and len(result["choices"]) > 0:
        content = result["choices"][0]["message"]["content"]
        return safe_parse_json(content)
    else:
        return {"error": "No response from AI."}
    