"""
pip install anthropic
"""

from anthropic import Anthropic
import os

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=200,
    messages=[
        {
            "role": "user",
            "content": "Explain how vector databases work in simple terms.",
        }
    ],
)

print(response.content[0].text)
