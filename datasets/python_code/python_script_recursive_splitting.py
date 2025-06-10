import os
import random
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Step 1: Define a function to load a random text document
def load_random_text_document(directory):
    """Loads a random text document from the specified directory."""
    files = [f for f in os.listdir(directory) if f.endswith('.txt')]
    if not files:
        raise FileNotFoundError("No text files found in the directory.")
    random_file = random.choice(files)
    with open(os.path.join(directory, random_file), 'r', encoding='utf-8') as file:
        return file.read(), random_file

# Step 2: Split the document using RecursiveCharacterTextSplitter
def split_document(text, chunk_size=1000, chunk_overlap=200):
    """Splits the text document into chunks using RecursiveCharacterTextSplitter."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap
    )
    return splitter.split_text(text)

# Step 3: Main script
if __name__ == "__main__":
    # Specify the directory containing text files
    text_directory = "./text_documents"  # Update this path as needed

    try:
        # Load a random text document
        document, filename = load_random_text_document(text_directory)
        print(f"Loaded document: {filename}")

        # Split the document
        chunks = split_document(document)
        print(f"Document split into {len(chunks)} chunks.")

        # Display the first few chunks
        for i, chunk in enumerate(chunks[:5]):
            print(f"\nChunk {i + 1}:")
            print(chunk)

    except Exception as e:
        print(f"An error occurred: {e}")
