"""
pip install ollama
"""

import ollama


def generate_response_with_ollama(
    context: str, question: str, model: str = "llama2"
) -> str:
    prompt = f"""
    Based on the following context, answer the question.

    Context:
    {context}

    Question:
    {question}

    Answer:
    """

    response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]


# Example usage
context = (
    "Natural language processing (NLP) is a field of AI "
    "focused on interaction between computers and language."
)
question = "What is NLP?"

answer = generate_response_with_ollama(context, question)
print(answer)
