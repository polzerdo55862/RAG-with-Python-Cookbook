import chromadb
from openai import OpenAI
import os


def retrieve_context(query, collection, client, embedding_model, top_k=5):
    response = client.embeddings.create(model=embedding_model, input=query)
    query_embedding = response.data[0].embedding
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
    return results["documents"][0]




def generate_response(query, context_docs, client, model, temperature, history):
    context = "\n\n---\n\n".join(context_docs)
    prompt = f"CONTEXT:\n{context}\n\nQUESTION: {query}"
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        # Include last 6 messages (3 turns) to provide conversational context
        # without exceeding token limits. Adjust based on your use case.
        *history[-6:],
        {"role": "user", "content": prompt},
    ]
    response = client.chat.completions.create(
        model=model, messages=messages, temperature=temperature, max_tokens=1000
    )
    return response.choices[0].message.content




if __name__ == "__main__":
    CHROMA_DB_DIR = "./chroma_db_dir"
    COLLECTION_NAME = "harry_potter_kb"
    OPENAI_API_KEY = os.environ[
        "OPENAI_API_KEY"
    ]  # Load OpenAI API key from environment variable
    EMBEDDING_MODEL = "text-embedding-ada-002"
    CHAT_MODEL = "gpt-3.5-turbo"
    TEMPERATURE = 0.2
    TOP_K_RESULTS = 5

    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
    collection = chroma_client.get_collection(name=COLLECTION_NAME)
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    conversation_history = []
    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ["quit", "exit", "bye"]:
            break
        context_docs = retrieve_context(
            user_input, collection, openai_client, EMBEDDING_MODEL, TOP_K_RESULTS
        )
        response = generate_response(
            user_input,
            context_docs,
            openai_client,
            CHAT_MODEL,
            TEMPERATURE,
            conversation_history,
        )
        conversation_history.append({"role": "user", "content": user_input})
        conversation_history.append({"role": "assistant", "content": response})
        print("Bot:", response)
