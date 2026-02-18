import streamlit as st
import os
from vanna.openai import OpenAI_Chat
from vanna.chromadb import ChromaDB_VectorStore
from openai import OpenAI

class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

# Initialize Vanna
if "vn" not in st.session_state:
    st.session_state.vn = MyVanna({
        "api_key": os.environ.get("OPENAI_API_KEY"),
        "model": "gpt-4.1",
        "path": "./chroma_db"
    })
    st.session_state.vn.connect_to_sqlite("bookstore.db")

    # Train on database schema
    ddl_df = st.session_state.vn.run_sql("SELECT sql FROM sqlite_master WHERE sql IS NOT NULL")
    for ddl in ddl_df["sql"]:
        st.session_state.vn.train(ddl=ddl)

st.title("SQL Chat App")

# Chat interface
if prompt := st.chat_input("Ask about the bookstore"):
    # Generate and run SQL
    sql = st.session_state.vn.generate_sql(prompt)
    result = st.session_state.vn.run_sql(sql)

    # Generate answer
    client = OpenAI()
    answer = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": f"Answer based on this data: {result}\nQuestion: {prompt}"}]
    ).choices[0].message.content

    # Display
    st.chat_message("user").write(prompt)
    st.chat_message("assistant").write(answer)
    with st.expander("SQL Result"):
        st.write(result)
