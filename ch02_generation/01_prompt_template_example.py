"""
Prompt Engineering Example
Shows how to create a basic prompt template for RAG applications
"""

# define the prompt template
template = """
You are a chat bot who loves to help people! Given the following context sections, answer the
question using only the given context. If you are unsure and the answer is not
explicitly written in the documentation, say "Sorry, I don't know how to help with that."

Context sections:
{context}

Question:
{users_question}

Answer:
"""

prompt = PromptTemplate(
    template=template, input_variables=["context", "users_question"]
)

# fill the prompt template
prompt_text = prompt.format(context=context, users_question=users_question)
llm(prompt_text)
