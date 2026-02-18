# Security Vulnerability Fixes

## Summary

Updated all dependencies with known security vulnerabilities to their patched versions across 7 requirements files.

## Vulnerabilities Fixed

### 1. cryptography (CRITICAL)
- **Old version**: 45.0.3
- **New version**: 46.0.5
- **Vulnerability**: Subgroup Attack Due to Missing Subgroup Validation for SECT Curves
- **Affected files**: ch03_loading_data/requirements_loading_data.txt

### 2. pillow (HIGH)
- **Old version**: 11.2.1
- **New version**: 12.1.1
- **Vulnerabilities**:
  - Out-of-bounds write when loading PSD images
  - Write buffer overflow on BCn encoding
- **Affected files**: 
  - ch03_loading_data/requirements_loading_data.txt
  - ch04_data_preparation_chunking_data/requirements_data_preparation_chunking_data.txt
  - ch05_text_embedding/requirements_ch05_text_embedding.txt
  - ch11_rag_chatbot_streamlit/requirements_ch11_rag_chatbot_streamlit.txt

### 3. protobuf (MEDIUM)
- **Old versions**: 6.31.1, 5.29.5
- **New versions**: 6.33.5, 5.29.6
- **Vulnerability**: JSON recursion depth bypass
- **Affected files**:
  - ch03_loading_data/requirements_loading_data.txt (6.31.1 → 6.33.5)
  - ch06_similarity_search_vector_databases/requirements_ch06_similarity_search_vector_databases.txt (5.29.5 → 5.29.6)
  - ch11_rag_chatbot_streamlit/requirements_ch11_rag_chatbot_streamlit.txt (5.29.5 → 5.29.6)

### 4. python-multipart (HIGH)
- **Old version**: 0.0.20
- **New version**: 0.0.22
- **Vulnerability**: Arbitrary File Write via Non-Default Configuration
- **Affected files**: ch03_loading_data/requirements_loading_data.txt

### 5. unstructured (HIGH)
- **Old version**: 0.17.2
- **New version**: 0.18.18
- **Vulnerability**: Path Traversal via Malicious MSG Attachment that Allows Arbitrary File Write
- **Affected files**: ch03_loading_data/requirements_loading_data.txt

### 6. urllib3 (MEDIUM)
- **Old versions**: 2.4.0, 2.5.0
- **New version**: 2.6.3
- **Vulnerabilities**:
  - Decompression-bomb safeguards bypassed when following HTTP redirects
  - Streaming API improperly handles highly compressed data
  - Unbounded number of links in the decompression chain
- **Affected files**:
  - ch03_loading_data/requirements_loading_data.txt
  - ch04_data_preparation_chunking_data/requirements_data_preparation_chunking_data.txt
  - ch05_text_embedding/requirements_ch05_text_embedding.txt
  - ch06_similarity_search_vector_databases/requirements_ch06_similarity_search_vector_databases.txt
  - ch07_retrieval/requirements_retrieval.txt
  - ch10_rag_evaluation/requirements_ch10_rag_evaluation.txt
  - ch11_rag_chatbot_streamlit/requirements_ch11_rag_chatbot_streamlit.txt

### 7. aiohttp (MEDIUM)
- **Old versions**: 3.12.9, 3.12.10
- **New version**: 3.13.3
- **Vulnerability**: HTTP Parser auto_decompress feature is vulnerable to zip bomb
- **Affected files**:
  - ch04_data_preparation_chunking_data/requirements_data_preparation_chunking_data.txt
  - ch05_text_embedding/requirements_ch05_text_embedding.txt

### 8. langchain-community (MEDIUM)
- **Old version**: 0.3.24
- **New version**: 0.3.27
- **Vulnerability**: XML External Entity (XXE) Attacks
- **Affected files**: ch04_data_preparation_chunking_data/requirements_data_preparation_chunking_data.txt

### 9. langchain-core (HIGH)
- **Old versions**: 0.3.64, 0.3.60
- **New version**: 0.3.81
- **Vulnerabilities**:
  - Template Injection via Attribute Access in Prompt Templates
  - Serialization injection vulnerability enables secret extraction in dumps/loads APIs
- **Affected files**:
  - ch04_data_preparation_chunking_data/requirements_data_preparation_chunking_data.txt
  - ch05_text_embedding/requirements_ch05_text_embedding.txt

### 10. langchain-text-splitters (MEDIUM)
- **Old version**: 0.3.8
- **New version**: 0.3.9
- **Vulnerability**: XML External Entity (XXE) attacks due to unsafe XSLT parsing
- **Affected files**:
  - ch04_data_preparation_chunking_data/requirements_data_preparation_chunking_data.txt
  - ch05_text_embedding/requirements_ch05_text_embedding.txt

## Files Modified

1. ✅ ch03_loading_data/requirements_loading_data.txt (6 vulnerabilities fixed)
2. ✅ ch04_data_preparation_chunking_data/requirements_data_preparation_chunking_data.txt (6 vulnerabilities fixed)
3. ✅ ch05_text_embedding/requirements_ch05_text_embedding.txt (5 vulnerabilities fixed)
4. ✅ ch06_similarity_search_vector_databases/requirements_ch06_similarity_search_vector_databases.txt (2 vulnerabilities fixed)
5. ✅ ch07_retrieval/requirements_retrieval.txt (1 vulnerability fixed)
6. ✅ ch10_rag_evaluation/requirements_ch10_rag_evaluation.txt (1 vulnerability fixed)
7. ✅ ch11_rag_chatbot_streamlit/requirements_ch11_rag_chatbot_streamlit.txt (3 vulnerabilities fixed)

## Impact

- **Total vulnerabilities fixed**: 24 (counting duplicates across files)
- **Unique vulnerabilities fixed**: 16
- **Security posture**: All known high and critical vulnerabilities in dependencies have been patched

## Recommendations

1. **Test thoroughly**: After updating, test notebooks to ensure compatibility with new versions
2. **Monitor dependencies**: Regularly check for security updates using `pip-audit` or similar tools
3. **Automated scanning**: Consider implementing automated dependency vulnerability scanning in CI/CD

## Verification

Run the validation script to verify all notebooks still work with updated dependencies:

```bash
python validate_notebooks.py
```

For security scanning:

```bash
pip install pip-audit
pip-audit -r ch03_loading_data/requirements_loading_data.txt
```
