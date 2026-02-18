import streamlit as st

with st.chat_message("user"):
    st.write("Hello, I am a user message.")

with st.chat_message("assistant"):
    st.write("Hello, I am an assistant message.")
