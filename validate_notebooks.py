#!/usr/bin/env python3
"""
Enhanced script to validate Jupyter notebooks can be executed.
This script will:
1. Check syntax and parse notebooks
2. Validate all imports can be resolved
3. Create a test report with recommendations
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Set
import nbformat

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

# Standard library modules that don't need installation
STDLIB_MODULES = {
    '__future__', 'abc', 'argparse', 'asyncio', 'base64', 'collections', 
    'contextlib', 'copy', 'dataclasses', 'datetime', 'decimal', 'enum',
    'functools', 'getpass', 'glob', 'hashlib', 'http', 'io', 'itertools',
    'json', 'logging', 'math', 'mimetypes', 'os', 'pathlib', 'pickle',
    'platform', 'pprint', 'random', 're', 'shutil', 'socket', 'statistics', 'string',
    'subprocess', 'sys', 'tempfile', 'textwrap', 'threading', 'time', 
    'traceback', 'typing', 'unittest', 'urllib', 'uuid', 'warnings', 'weakref',
    'xml', 'zipfile',
}


def get_chapter_from_path(notebook_path: str) -> str:
    """Extract chapter directory from notebook path."""
    return notebook_path.split('/')[0]


def get_requirements_file(notebook_path: str) -> str:
    """Get requirements file path for a notebook."""
    chapter = get_chapter_from_path(notebook_path)
    return REQUIREMENTS_MAP.get(chapter)


def parse_requirements_file(req_file: str) -> Set[str]:
    """Parse requirements file and extract package names."""
    packages = set()
    if not os.path.exists(req_file):
        return packages
    
    try:
        with open(req_file, 'r', encoding='utf-8-sig', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Extract package name (before ==, >=, <=, etc.)
                    pkg = line.split('==')[0].split('>=')[0].split('<=')[0].split('[')[0].strip()
                    if pkg:
                        # Convert package name to import name
                        # Common conversions
                        import_name = pkg.lower().replace('-', '_').replace('.', '_')
                        packages.add(import_name)
                        # Also add the original in case it's different
                        if pkg != import_name:
                            packages.add(pkg.lower())
    except Exception as e:
        print(f"Warning: Could not parse requirements file {req_file}: {e}")
    
    return packages


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
                # Skip comments and magic commands
                if line.startswith('#') or line.startswith('%') or line.startswith('!'):
                    continue
                    
                # Basic import detection
                if line.startswith('import ') or line.startswith('from '):
                    # Extract package name
                    if line.startswith('import '):
                        parts = line.replace('import ', '').split()
                        if parts:
                            pkg = parts[0].split('.')[0].split(',')[0]
                            imports.add(pkg)
                    elif line.startswith('from '):
                        parts = line.replace('from ', '').split()
                        if parts:
                            pkg = parts[0].split('.')[0]
                            imports.add(pkg)
    
    return sorted(list(imports))


def check_for_api_keys(notebook_path: str) -> List[str]:
    """Check if notebook requires API keys."""
    with open(notebook_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    api_key_patterns = [
        ('OPENAI_API_KEY', 'OpenAI API Key'),
        ('ANTHROPIC_API_KEY', 'Anthropic API Key'),
        ('COHERE_API_KEY', 'Cohere API Key'),
        ('HUGGINGFACE_API_KEY', 'HuggingFace API Key'),
        ('GOOGLE_API_KEY', 'Google API Key'),
        ('NEO4J_URI', 'Neo4j Database URI'),
        ('NEO4J_PASSWORD', 'Neo4j Database Password'),
        ('NEO4J_USERNAME', 'Neo4j Username'),
    ]
    
    required_keys = []
    for pattern, description in api_key_patterns:
        if pattern in content:
            required_keys.append(description)
    
    return required_keys


def check_missing_dependencies(notebook_imports: List[str], requirements_packages: Set[str]) -> List[str]:
    """Check if any imports are not covered by requirements."""
    missing = []
    
    # Map of common import names to package names
    import_to_package = {
        'PIL': 'pillow',
        'cv2': 'opencv_python',
        'sklearn': 'scikit_learn',
        'dotenv': 'python_dotenv',
        'google': 'google_colab',  # Special case - Colab-only, not in requirements
        'rank_bm25': 'rank_bm25',
        'pdf2image': 'pdf2image',
        'pytesseract': 'pytesseract',
        'sqlalchemy': 'sqlalchemy',
        'psycopg2': 'psycopg2_binary',
        'IPython': 'ipython',
        'geopy': 'geopy',
        'agents': 'openai',  # OpenAI SDK includes agents
        'docx': 'python_docx',
        'faiss': 'faiss_cpu',
    }
    
    # Special imports that don't need to be in requirements (Colab-specific, built-ins, etc.)
    SPECIAL_IMPORTS = {'google'}  # google.colab is Colab-only
    
    for imp in notebook_imports:
        if imp in STDLIB_MODULES:
            continue
        
        # Skip special imports (like google.colab)
        if imp in SPECIAL_IMPORTS:
            continue
        
        # Check direct match
        import_lower = imp.lower().replace('-', '_')
        if import_lower in requirements_packages:
            continue
        
        # Check with common package mappings
        if imp in import_to_package:
            pkg = import_to_package[imp]
            if pkg.lower().replace('-', '_') in requirements_packages:
                continue
        
        # Check if it's a submodule of a known package
        found = False
        for req_pkg in requirements_packages:
            if import_lower.startswith(req_pkg + '_') or import_lower.startswith(req_pkg):
                found = True
                break
        
        if not found:
            missing.append(imp)
    
    return missing


def validate_notebook(notebook_path: str) -> Dict:
    """Validate a single notebook."""
    result = {
        'exists': False,
        'syntax_ok': False,
        'requirements_file': None,
        'requirements_exist': False,
        'imports': [],
        'api_keys': [],
        'missing_dependencies': [],
        'warnings': [],
        'status': 'unknown'
    }
    
    # Check if notebook exists
    if not os.path.exists(notebook_path):
        result['status'] = 'missing'
        result['warnings'].append("Notebook file not found")
        return result
    
    result['exists'] = True
    
    # Check syntax
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        result['syntax_ok'] = True
    except Exception as e:
        result['status'] = 'syntax_error'
        result['warnings'].append(f"Syntax error: {str(e)}")
        return result
    
    # Check requirements file
    req_file = get_requirements_file(notebook_path)
    result['requirements_file'] = req_file
    
    if req_file and os.path.exists(req_file):
        result['requirements_exist'] = True
    else:
        result['warnings'].append("Requirements file not found")
    
    # Analyze imports
    try:
        imports = analyze_notebook_imports(notebook_path)
        result['imports'] = imports
    except Exception as e:
        result['warnings'].append(f"Could not analyze imports: {str(e)}")
    
    # Check for API keys
    try:
        api_keys = check_for_api_keys(notebook_path)
        result['api_keys'] = api_keys
    except Exception as e:
        result['warnings'].append(f"Could not check for API keys: {str(e)}")
    
    # Check for missing dependencies
    if result['requirements_exist'] and result['imports']:
        req_packages = parse_requirements_file(req_file)
        missing = check_missing_dependencies(result['imports'], req_packages)
        result['missing_dependencies'] = missing
        
        if missing:
            result['warnings'].append(f"Potentially missing dependencies: {', '.join(missing)}")
    
    # Determine overall status
    if result['warnings']:
        result['status'] = 'warning'
    else:
        result['status'] = 'ok'
    
    return result


def main():
    """Main validation function."""
    print("=" * 80)
    print("COMPREHENSIVE JUPYTER NOTEBOOK VALIDATION REPORT")
    print("=" * 80)
    print()
    
    results = {}
    summary = {
        'total': len(NOTEBOOKS),
        'ok': 0,
        'warning': 0,
        'error': 0,
        'missing': 0
    }
    
    for notebook_path in NOTEBOOKS:
        print(f"\nValidating: {notebook_path}")
        result = validate_notebook(notebook_path)
        results[notebook_path] = result
        
        # Update summary
        summary[result['status']] += 1
        
        # Print status
        if result['status'] == 'ok':
            print(f"  ✓ Status: OK")
        elif result['status'] == 'warning':
            print(f"  ⚠️  Status: WARNING")
            for warning in result['warnings']:
                print(f"     - {warning}")
        elif result['status'] == 'missing':
            print(f"  ❌ Status: MISSING")
        elif result['status'] == 'syntax_error':
            print(f"  ❌ Status: SYNTAX ERROR")
        
        if result['api_keys']:
            print(f"  🔑 Required: {', '.join(result['api_keys'])}")
    
    # Print summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    print(f"Total notebooks: {summary['total']}")
    print(f"✓ OK: {summary['ok']}")
    print(f"⚠️  Warnings: {summary['warning']}")
    print(f"❌ Errors: {summary['error']}")
    print(f"❌ Missing: {summary['missing']}")
    
    # Generate recommendations
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    
    all_api_keys = set()
    for notebook_path, result in results.items():
        if result['api_keys']:
            all_api_keys.update(result['api_keys'])
    
    if all_api_keys:
        print("\n📋 Required API Keys for Full Execution:")
        for key in sorted(all_api_keys):
            print(f"   - {key}")
        print("\n   Set these in a .env file or as environment variables before running notebooks.")
    
    # Check for notebooks with warnings
    notebooks_with_warnings = [
        (path, result) for path, result in results.items() 
        if result['status'] == 'warning'
    ]
    
    if notebooks_with_warnings:
        print(f"\n⚠️  {len(notebooks_with_warnings)} Notebook(s) with Warnings:")
        for path, result in notebooks_with_warnings:
            print(f"\n   {path}:")
            for warning in result['warnings']:
                print(f"      - {warning}")
    
    # Save detailed results
    output_file = 'notebook_validation_report.json'
    with open(output_file, 'w') as f:
        json.dump({
            'summary': summary,
            'results': results
        }, f, indent=2)
    print(f"\n📄 Detailed validation report saved to: {output_file}")
    
    # Exit code based on results
    if summary['error'] > 0 or summary['missing'] > 0:
        print("\n❌ Validation completed with errors")
        return 1
    elif summary['warning'] > 0:
        print("\n⚠️  Validation completed with warnings")
        return 0
    else:
        print("\n✓ All notebooks passed validation!")
        return 0


if __name__ == '__main__':
    sys.exit(main())
