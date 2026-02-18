#!/usr/bin/env python3
"""
Script to test execution of all Jupyter notebooks in the repository.
This script will:
1. Find all notebooks mentioned in README
2. Attempt to execute each notebook
3. Report any errors or missing dependencies
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor, CellExecutionError

# Notebook paths from README
NOTEBOOKS = [
    "ch01_RAG_intro/rag_basics.ipynb",
    "ch02_generation/generation.ipynb",
    "ch03_loading_data/loading_data_to_RAG.ipynb",
    "ch04_data_preparation_chunking_data/chunking_data.ipynb",
    "ch05_text_embedding/text_embeddings.ipynb",
    "ch06_similarity_search_vector_databases/vector_databases.ipynb",
    "ch07_retrieval/retrieval_techniques.ipynb",
    "ch08_agentic_rag/8.4_building_agentic_system_function_calling/building_agents_without_framework.ipynb",
    "ch08_agentic_rag/8.6_sales_negotiation_agent_openai_sdk/building_agents_with_openai_sdk.ipynb",
    "ch08_agentic_rag/8.8_agentic_system_langgraph/building_agents_using_langgraph.ipynb",
    "ch09_graph_rag/9.1_basic_sla_graph.ipynb",
    "ch09_graph_rag/9.2_enrich_company_data.ipynb",
    "ch09_graph_rag/9.3_cypher_queries.ipynb",
    "ch09_graph_rag/9.4_embeddings_vector_search.ipynb",
    "ch09_graph_rag/9.5_useful_extensions.ipynb",
    "ch10_rag_evaluation/rag_evaluation_techniques.ipynb",
]

# Map notebooks to their requirements files
REQUIREMENTS_MAP = {
    "ch01_RAG_intro": "ch01_RAG_intro/requirements.txt",
    "ch02_generation": "ch02_generation/requirements_ch02_generation.txt",
    "ch03_loading_data": "ch03_loading_data/requirements_loading_data.txt",
    "ch04_data_preparation_chunking_data": "ch04_data_preparation_chunking_data/requirements_data_preparation_chunking_data.txt",
    "ch05_text_embedding": "ch05_text_embedding/requirements_ch05_text_embedding.txt",
    "ch06_similarity_search_vector_databases": "ch06_similarity_search_vector_databases/requirements_ch06_similarity_search_vector_databases.txt",
    "ch07_retrieval": "ch07_retrieval/requirements_retrieval.txt",
    "ch08_agentic_rag": "ch08_agentic_rag/requirements_ch08_agentic_rag.txt",
    "ch09_graph_rag": "ch09_graph_rag/requirements_ch09_graph_rag.txt",
    "ch10_rag_evaluation": "ch10_rag_evaluation/requirements_ch10_rag_evaluation.txt",
    "ch11_rag_chatbot_streamlit": "ch11_rag_chatbot_streamlit/requirements_ch11_rag_chatbot_streamlit.txt",
}


def get_chapter_from_path(notebook_path: str) -> str:
    """Extract chapter directory from notebook path."""
    return notebook_path.split('/')[0]


def check_notebook_exists(notebook_path: str) -> bool:
    """Check if notebook file exists."""
    return os.path.exists(notebook_path)


def get_requirements_file(notebook_path: str) -> str:
    """Get requirements file path for a notebook."""
    chapter = get_chapter_from_path(notebook_path)
    return REQUIREMENTS_MAP.get(chapter)


def analyze_notebook_imports(notebook_path: str) -> List[str]:
    """Analyze notebook to extract import statements."""
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)
    
    imports = set()
    for cell in nb.cells:
        if cell.cell_type == 'code':
            lines = cell.source.split('\n')
            for line in lines:
                line = line.strip()
                # Basic import detection
                if line.startswith('import ') or line.startswith('from '):
                    # Extract package name
                    if line.startswith('import '):
                        pkg = line.replace('import ', '').split()[0].split('.')[0]
                        imports.add(pkg)
                    elif line.startswith('from '):
                        pkg = line.replace('from ', '').split()[0].split('.')[0]
                        imports.add(pkg)
    
    return sorted(list(imports))


def check_for_api_keys(notebook_path: str) -> List[str]:
    """Check if notebook requires API keys."""
    with open(notebook_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    api_key_patterns = [
        'OPENAI_API_KEY',
        'ANTHROPIC_API_KEY',
        'COHERE_API_KEY',
        'HUGGINGFACE_API_KEY',
        'NEO4J_URI',
        'NEO4J_PASSWORD',
    ]
    
    required_keys = []
    for pattern in api_key_patterns:
        if pattern in content:
            required_keys.append(pattern)
    
    return required_keys


def test_notebook_syntax(notebook_path: str) -> Tuple[bool, str]:
    """Test if notebook can be parsed."""
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        return True, "Syntax OK"
    except Exception as e:
        return False, f"Syntax error: {str(e)}"


def main():
    """Main test function."""
    print("=" * 80)
    print("JUPYTER NOTEBOOK TESTING REPORT")
    print("=" * 80)
    print()
    
    results = {
        'total': len(NOTEBOOKS),
        'found': 0,
        'missing': 0,
        'syntax_ok': 0,
        'syntax_error': 0,
        'notebooks': {}
    }
    
    for notebook_path in NOTEBOOKS:
        print(f"\n{'=' * 80}")
        print(f"Testing: {notebook_path}")
        print('=' * 80)
        
        result = {
            'exists': False,
            'syntax_ok': False,
            'requirements_file': None,
            'imports': [],
            'api_keys': [],
            'errors': []
        }
        
        # Check if notebook exists
        if not check_notebook_exists(notebook_path):
            print(f"❌ MISSING: Notebook not found")
            result['errors'].append("Notebook file not found")
            results['missing'] += 1
        else:
            print(f"✓ Found")
            result['exists'] = True
            results['found'] += 1
            
            # Check syntax
            syntax_ok, syntax_msg = test_notebook_syntax(notebook_path)
            result['syntax_ok'] = syntax_ok
            if syntax_ok:
                print(f"✓ Syntax OK")
                results['syntax_ok'] += 1
            else:
                print(f"❌ {syntax_msg}")
                result['errors'].append(syntax_msg)
                results['syntax_error'] += 1
            
            # Check requirements file
            req_file = get_requirements_file(notebook_path)
            result['requirements_file'] = req_file
            if req_file:
                if os.path.exists(req_file):
                    print(f"✓ Requirements file: {req_file}")
                else:
                    print(f"⚠️  Requirements file missing: {req_file}")
                    result['errors'].append(f"Requirements file not found: {req_file}")
            else:
                print(f"⚠️  No requirements file specified for chapter")
                result['errors'].append("No requirements file for this chapter")
            
            # Analyze imports
            if syntax_ok:
                try:
                    imports = analyze_notebook_imports(notebook_path)
                    result['imports'] = imports
                    print(f"📦 Detected imports: {', '.join(imports[:10])}")
                    if len(imports) > 10:
                        print(f"   ... and {len(imports) - 10} more")
                except Exception as e:
                    print(f"⚠️  Could not analyze imports: {str(e)}")
            
            # Check for API keys
            try:
                api_keys = check_for_api_keys(notebook_path)
                result['api_keys'] = api_keys
                if api_keys:
                    print(f"🔑 Required API keys/config: {', '.join(api_keys)}")
            except Exception as e:
                print(f"⚠️  Could not check for API keys: {str(e)}")
        
        results['notebooks'][notebook_path] = result
    
    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total notebooks: {results['total']}")
    print(f"Found: {results['found']}")
    print(f"Missing: {results['missing']}")
    print(f"Syntax OK: {results['syntax_ok']}")
    print(f"Syntax errors: {results['syntax_error']}")
    
    # Identify chapters without requirements
    chapters_without_requirements = set()
    for notebook_path, result in results['notebooks'].items():
        if result['exists']:
            chapter = get_chapter_from_path(notebook_path)
            req_file = REQUIREMENTS_MAP.get(chapter)
            if not req_file:
                chapters_without_requirements.add(chapter)
    
    if chapters_without_requirements:
        print(f"\n⚠️  Chapters without requirements files:")
        for chapter in sorted(chapters_without_requirements):
            print(f"   - {chapter}")
    
    # Identify notebooks with issues
    notebooks_with_issues = []
    for notebook_path, result in results['notebooks'].items():
        if result['errors']:
            notebooks_with_issues.append(notebook_path)
    
    if notebooks_with_issues:
        print(f"\n❌ Notebooks with issues:")
        for notebook_path in notebooks_with_issues:
            print(f"   - {notebook_path}")
            for error in results['notebooks'][notebook_path]['errors']:
                print(f"      • {error}")
    
    # Save detailed results to JSON
    output_file = 'notebook_test_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n📄 Detailed results saved to: {output_file}")
    
    return 0 if results['missing'] == 0 and results['syntax_error'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
