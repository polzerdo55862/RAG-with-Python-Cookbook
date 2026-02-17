"""
pip install openai
"""

from openai import OpenAI

# Step 1: Create the client
client = OpenAI()  # Uses OPENAI_API_KEY from environment

# Step 2: Define your messages
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is 2 + 2?"},
]

# Step 3: Send request and get response
response = client.chat.completions.create(model="gpt-4", messages=messages)

# Step 4: Extract the answer
answer = response.choices[0].message.content
print(answer)  # Output: "4"
