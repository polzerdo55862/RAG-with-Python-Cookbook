"""
pip install openai
"""

from openai import OpenAI


def ask_with_context(context, question):
    client = OpenAI()

    messages = [
        {"role": "system", "content": "Answer based only on the provided context."},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{question}"},
    ]

    response = client.chat.completions.create(
        model="gpt-5", messages=messages  # Using latest model
    )

    return response.choices[0].message.content


# Usage
context = "RAG stands for Retrieval-Augmented Generation."
question = "What does RAG stand for?"
answer = ask_with_context(context, question)
print(answer)
