"""
Running Local LLMs with Ollama
Shows how to use locally hosted models via Ollama with the OpenAI SDK

pip install openai
"""

from openai import OpenAI

# Point the client to your local Ollama server
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # Ollama doesn't require a real key, but the SDK expects one
)

# Send a chat completion request
response = client.chat.completions.create(
    model="quen3:4b",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is retrieval-augmented generation?"},
    ],
)

print(response.choices[0].message.content)
