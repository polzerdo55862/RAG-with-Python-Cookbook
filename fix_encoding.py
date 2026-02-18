#!/usr/bin/env python3
"""
Convert UTF-16 encoded requirements files to UTF-8.
This fixes encoding issues that prevent proper parsing.
"""

import os
import sys
from pathlib import Path

# Requirements files that need conversion
FILES_TO_CONVERT = [
    "ch03_loading_data/requirements_loading_data.txt",
    "ch04_data_preparation_chunking_data/requirements_data_preparation_chunking_data.txt",
    "ch05_text_embedding/requirements_ch05_text_embedding.txt",
    "ch06_similarity_search_vector_databases/requirements_ch06_similarity_search_vector_databases.txt",
    "ch07_retrieval/requirements_retrieval.txt",
    "ch10_rag_evaluation/requirements_ch10_rag_evaluation.txt",
    "ch11_rag_chatbot_streamlit/requirements_ch11_rag_chatbot_streamlit.txt",
]


def convert_file_encoding(file_path: str):
    """Convert a file from UTF-16 to UTF-8."""
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    try:
        # Read with UTF-16 encoding
        with open(file_path, 'r', encoding='utf-16-le') as f:
            content = f.read()
        
        # Write with UTF-8 encoding
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ Converted: {file_path}")
        return True
    except Exception as e:
        print(f"❌ Error converting {file_path}: {e}")
        return False


def main():
    """Main conversion function."""
    print("=" * 80)
    print("CONVERTING REQUIREMENTS FILES TO UTF-8")
    print("=" * 80)
    print()
    
    success_count = 0
    fail_count = 0
    
    for file_path in FILES_TO_CONVERT:
        if convert_file_encoding(file_path):
            success_count += 1
        else:
            fail_count += 1
    
    print()
    print("=" * 80)
    print("CONVERSION SUMMARY")
    print("=" * 80)
    print(f"✓ Successfully converted: {success_count}")
    print(f"❌ Failed: {fail_count}")
    
    if fail_count == 0:
        print("\n✓ All files converted successfully!")
        return 0
    else:
        print("\n⚠️  Some files failed to convert")
        return 1


if __name__ == '__main__':
    sys.exit(main())
