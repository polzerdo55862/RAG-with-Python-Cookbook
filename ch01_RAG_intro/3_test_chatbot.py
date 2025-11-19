"""
RAG Chatbot Test Script - Automated Testing

This script demonstrates automated testing of the RAG chatbot without manual interaction.
Useful for:
- Quick verification that the system works end-to-end
- Demonstrating RAG capabilities with predefined questions
- Debugging and development

Usage:
    python 3_test_chatbot.py

Requirements:
    - Vector database must exist (run 1_ingest_data.py first)
"""

import sys
import chromadb
from openai import OpenAI
from dotenv import load_dotenv
from config import *

load_dotenv()

# Import retrieval and generation functions from chatbot
from importlib import import_module

chatbot = import_module("2_chatbot")
retrieve_context = chatbot.retrieve_context
generate_response = chatbot.generate_response


def main():
    """Run automated tests with sample questions."""
    test_queries = [
        "Who is Harry Potter?",
        "What happened at the zoo with the snake?",
        "Tell me about the Dursleys",
        "What is special about Harry's scar?",
    ]

    print("=" * 70)
    print("RAG CHATBOT - AUTOMATED TEST")
    print("=" * 70)

    if not CHROMA_DB_DIR.exists():
        print("\n❌ Error: Vector database not found!")
        print("Run '1_ingest_data.py' first.\n")
        sys.exit(1)

    # Initialize components
    print("\nInitializing...")
    chroma_client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
    collection = chroma_client.get_collection(name=COLLECTION_NAME)
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    conversation_history = []

    print(f"✓ Ready ({collection.count()} documents)\n")
    print("=" * 70)

    # Test each question
    for i, query in enumerate(test_queries, 1):
        print(f"\n[Test {i}/{len(test_queries)}]")
        print(f"Q: {query}")
        print("-" * 70)

        try:
            # Retrieve and generate
            context = retrieve_context(
                query, collection, openai_client, EMBEDDING_MODEL
            )
            response = generate_response(
                query,
                context,
                openai_client,
                CHAT_MODEL,
                TEMPERATURE,
                conversation_history,
            )

            # Update history
            conversation_history.append({"role": "user", "content": query})
            conversation_history.append({"role": "assistant", "content": response})

            print(f"A: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")

        print("\n" + "=" * 70)

    print("\n✓ All tests completed!\n")


if __name__ == "__main__":
    main()
