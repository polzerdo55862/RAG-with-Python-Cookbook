import streamlit as st

st.set_page_config(layout="wide")

st.title("Welcome to the Streamlit App")

st.write("This is a simple Streamlit application deployed using Docker.")

st.sidebar.header("User Input")
user_input = st.sidebar.text_input("Enter your query:")

if user_input:
    st.write(f"You entered: {user_input}")

st.write("Feel free to explore the app!")