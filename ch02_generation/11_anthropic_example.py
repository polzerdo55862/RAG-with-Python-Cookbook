"""
pip install anthropic
"""

# tag::code_example[]
import os
from anthropic import Anthropic

client = Anthropic()
resp = client.messages.create(
    model="claude-4-5-sonnet-latest",
    max_tokens=200,
    messages=[{"role": "user", "content": "Say hi"}],
)
print(resp.content[0].text)
# end::code_example[]
