"""
pip install openai
"""

import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("GOOGLE_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

resp = client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=[{"role": "user", "content": "What is the capital of France?"}],
)

print(resp.choices[0].message.content)
