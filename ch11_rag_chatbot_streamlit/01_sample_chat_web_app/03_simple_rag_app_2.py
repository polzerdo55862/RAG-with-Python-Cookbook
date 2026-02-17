"""
Simple RAG Chat App with Streamlit

This is a basic demonstration of building a chat interface using Streamlit for a RAG
(Retrieval-Augmented Generation) application. The app provides:

- A chat-style user interface with message history
- Session state management to maintain conversation across reruns
- A simple mock RAG function that responds to user queries
- Chat input and message display using Streamlit's chat components

To run this app:
    streamlit run 03_simple_rag_app_2.py

The app will be available at http://localhost:8501

This serves as a foundation that can be extended with real RAG functionality,
including document retrieval, vector databases, and LLM integration.
"""

import streamlit as st

st.title("Simple RAG Chat App")

if "messages" not in st.session_state:
    st.session_state.messages = []


def simple_rag(query):
    if "hello" in query.lower():
        return "Hello! How can I help you?"
    elif "rag" in query.lower():
        return "RAG combines retrieval and generation for better responses."
    else:
        return f"You asked: '{query}'. A real RAG system would search documents and generate a response."


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    response = simple_rag(prompt)
    st.session_state.messages.append({"role": "assistant", "content": response})

    with st.chat_message("assistant"):
        st.markdown(response)
