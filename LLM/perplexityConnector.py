# README.md
# "model": "sonar"
# Input Tokens $1 Per 1M Tokens
# Output Tokens $1 Per 1M Tokens

import requests
import os
import json

print("Initialized")

# api_ker = os.environ.get("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")  # Or set directly: api_key = "YOUR_PERPLEXITY_API_KEY"
api_key = "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"  # Or set directly: api_key = "YOUR_PERPLEXITY_API_KEY"

#print(f"api_key: {api_key}")

url = "https://api.perplexity.ai/chat/completions"
payload = {
    "model": "sonar", 
    "messages": [
        #{"role": "system", "content": "Be precise and concise."},
        #{"role": "user", "content": "Explain the concept of Retrieval-Augmented Generation (RAG)."}
        {"role": "user", "content": "Whos the PM of India"}
    ],
    "max_tokens": 800,
    "temperature": 0.5
}
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

response = requests.post(url, headers=headers, json=payload)
# print("Status Code:", response.status_code)
# print("Raw Response:", response.text)
response_json = response.json()
# print(json.dumps(response_json, indent=2))
# print(response.json())
content = response_json.get("choices", [{}])[0].get("message", {}).get("content")

if content:
    print(content)
else:
    print("Content field not found in the response")


print("End")

