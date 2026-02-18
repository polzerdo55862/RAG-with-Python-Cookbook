import streamlit as st

st.title("Simple Chatbot")
user_input = st.text_input("You:")
if user_input:
    st.write(f"Bot: You said '{user_input}'!")
