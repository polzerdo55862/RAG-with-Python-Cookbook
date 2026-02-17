"""
pip install openai pydantic
"""

from pydantic import BaseModel
from openai import OpenAI

class Person(BaseModel):
    first_name: str
    last_name: str
    email: str
    age: int

client = OpenAI()

text = "My name is Sarah Johnson, I'm 34 years old. Email me at sarah.j@example.com"

response = client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "Extract person information."},
        {"role": "user", "content": text},
    ],
    response_format=Person,
)

person = response.choices[0].message.parsed
print(person.first_name)
print(person.email)
print(person.age)
