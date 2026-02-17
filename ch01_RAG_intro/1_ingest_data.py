def chunk_text(text, chunk_size, overlap):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        if end < len(text):
            break_point = text.rfind("\n\n", start, end)
            if break_point == -1:
                break_point = text.rfind(". ", start, end)
            if break_point != -1 and break_point > start:
                end = break_point + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end - overlap if end < len(text) else end

    return chunks




def generate_embeddings(texts, client, model):
    embeddings = []
    batch_size = 100

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        response = client.embeddings.create(model=model, input=batch)
        embeddings.extend([item.embedding for item in response.data])

    return embeddings




def ingest_to_chromadb(chunks, embeddings, db_path, collection_name):

    db_path.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(db_path))

    try:
        client.delete_collection(name=collection_name)
    except:
        pass

    collection = client.create_collection(
        name=collection_name, metadata={"description": "Harry Potter knowledge base"}
    )

    collection.add(
        ids=[f"chunk_{i}" for i in range(len(chunks))],
        embeddings=embeddings,
        documents=chunks,
        metadatas=[{"chunk_index": i} for i in range(len(chunks))],
    )

    return collection.count()




from pathlib import Path
from openai import OpenAI
import os


def main():
    KNOWLEDGE_BASE_FILE = "harry_potter.txt"  # Path to your knowledge base file
    CHUNK_SIZE = 1000  # Number of characters per chunk
    CHUNK_OVERLAP = 200  # Number of overlapping characters between chunks
    EMBEDDING_MODEL = "text-embedding-ada-002"  # OpenAI embedding model name
    CHROMA_DB_DIR = Path("chroma_db")  # Directory for ChromaDB persistence
    COLLECTION_NAME = "harry_potter_kb"  # Name of the ChromaDB collection

    with open(KNOWLEDGE_BASE_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)

    client = OpenAI(api_key=OPENAI_API_KEY)
    embeddings = generate_embeddings(chunks, client, EMBEDDING_MODEL)

    count = ingest_to_chromadb(chunks, embeddings, CHROMA_DB_DIR, COLLECTION_NAME)


if __name__ == "__main__":
    main()
