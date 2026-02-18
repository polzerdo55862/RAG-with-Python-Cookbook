# Notebook Testing Quick Start

This directory contains tools to validate and test all Jupyter notebooks in the repository.

## Quick Test

Run a quick validation of all notebooks:

```bash
python validate_notebooks.py
```

This will check:
- ✅ All notebooks exist and have valid syntax
- ✅ All requirements files are present
- ✅ All dependencies are covered
- 🔑 What API keys are needed

## Expected Output

```
================================================================================
VALIDATION SUMMARY
================================================================================
Total notebooks: 16
✓ OK: 16
⚠️  Warnings: 0
❌ Errors: 0
❌ Missing: 0

📋 Required API Keys for Full Execution:
   - Anthropic API Key
   - Google API Key
   - Neo4j Database Password
   - Neo4j Database URI
   - Neo4j Username
   - OpenAI API Key
```

## Running Individual Notebooks

1. **Install dependencies for the chapter**:
   ```bash
   pip install -r ch01_RAG_intro/requirements.txt
   ```

2. **Set up API keys** (choose one method):
   
   **Option A: Environment variables**
   ```bash
   export OPENAI_API_KEY=your_key_here
   ```
   
   **Option B: .env file**
   ```
   OPENAI_API_KEY=your_key_here
   ANTHROPIC_API_KEY=your_key_here
   ```

3. **Run the notebook**:
   ```bash
   jupyter notebook ch01_RAG_intro/rag_basics.ipynb
   ```

## For Colab Users

Simply click the "Open in Colab" badges in the README.md. The notebooks are designed to work seamlessly in Google Colab.

## Troubleshooting

**Q: Requirements file not found?**
A: Make sure you're in the repository root directory.

**Q: Encoding issues?**
A: All requirements files are now UTF-8. If you encounter issues, run:
```bash
python fix_encoding.py
```

**Q: Missing dependencies?**
A: Run validation to see what's needed:
```bash
python validate_notebooks.py
```

## Full Documentation

See [NOTEBOOK_TESTING.md](NOTEBOOK_TESTING.md) for comprehensive testing documentation.
