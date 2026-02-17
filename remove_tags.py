import os
import json
import re

files = [
    r'ch11_rag_chatbot_streamlit\03_entity_extraction_web_app\entity_extraction_web_app.py',
    r'ch11_rag_chatbot_streamlit\02_sql_chat_app\vanna_chat.py',
    r'ch11_rag_chatbot_streamlit\01_sample_chat_web_app\03_simple_rag_app_2.py',
    r'ch11_rag_chatbot_streamlit\01_sample_chat_web_app\app_helper_functions.py',
    r'ch11_rag_chatbot_streamlit\01_sample_chat_web_app\04_simple_rag_app_3.py',
    r'ch09_graph_rag\recipe01_basic_sla_graph.ipynb',
    r'ch08_agentic_rag\04_Langgraph_agents\building_agents_using_langgraph.ipynb',
    r'ch08_agentic_rag\05_asynchronous_python\book_snippet_asynchio.py',
    r'ch08_agentic_rag\03_MCP\02_create_a_web_agent_playwright.py',
    r'ch08_agentic_rag\03_MCP\01_connect_to_playwright.py',
    r'ch08_agentic_rag\02_OpenAI_SDK\building_agents_with_openai_sdk.ipynb',
    r'ch08_agentic_rag\01_Agents_with_Function_Calling\building_agents_without_framework.ipynb',
    r'ch10_rag_evaluation\rag_evaluation_techniques.ipynb',
    r'ch04_data_preparation_chunking_data\chunking_data.ipynb',
    r'ch02_generation\01_prompt_template_example.py',
    r'ch01_RAG_intro\1_ingest_data.py',
    r'ch02_generation\02_openai_chat_completion.py',
    r'ch02_generation\03_rag_with_context.py',
    r'ch05_text_embedding\text_embeddings.ipynb',
    r'ch02_generation\04_whisper_speech_to_text.py',
    r'ch01_RAG_intro\2_chatbot.py',
    r'ch05_text_embedding\text_embeddings.py',
    r'ch02_generation\05_anthropic_claude_example.py',
    r'ch02_generation\06_gemini_api_example.py',
    r'ch02_generation\07_ollama_local_llm.py',
    r'ch02_generation\08_ollama_model_comparison.py',
    r'ch02_generation\09_pydantic_structured_output_basic.py',
    r'ch06_similarity_search_vector_databases\vector_databases.ipynb',
    r'ch02_generation\11_anthropic_example.py',
    r'ch02_generation\10_pydantic_invoice_extraction.py',
    r'ch03_loading_data\loading_data_to_RAG.ipynb'
]

tag_pattern = re.compile(r'^# (?:tag|end)::[^\]]*\]\s*$')
modified_count = 0

for filepath in files:
    filepath = filepath.strip()
    if not os.path.exists(filepath):
        print(f"Skipping {filepath} (not found)")
        continue
    
    if filepath.endswith('.ipynb'):
        with open(filepath, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        modified = False
        for cell in notebook.get('cells', []):
            if cell.get('cell_type') == 'code':
                source = cell.get('source', [])
                if isinstance(source, list):
                    new_source = [line for line in source if not tag_pattern.match(line.rstrip())]
                    if len(new_source) != len(source):
                        cell['source'] = new_source
                        modified = True
        
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(notebook, f, indent=1, ensure_ascii=False)
                f.write('\n')
            modified_count += 1
            print(f"Modified {filepath}")
    else:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        new_lines = [line for line in lines if not tag_pattern.match(line.rstrip())]
        
        if len(new_lines) != len(lines):
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            modified_count += 1
            print(f"Modified {filepath}")

print(f'\nTotal: Modified {modified_count} files')
