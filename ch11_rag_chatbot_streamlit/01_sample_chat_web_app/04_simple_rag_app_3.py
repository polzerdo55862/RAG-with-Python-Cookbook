import streamlit as st
import os

st.title("My Streamlit RAG App")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


import app_helper_functions


def perform_rag(user_query):
    location_data = app_helper_functions.extract_the_city_and_country(user_query)
    latitude, longitude = app_helper_functions.get_coordinates_for_city(
        location_data["city"], location_data["country"]
    )
    weather_data = app_helper_functions.get_current_weather_open_meteo(
        latitude, longitude
    )
    prompt = app_helper_functions.create_weather_prompt(user_query, weather_data)
    response = app_helper_functions.send_prompt_to_llm(prompt)

    return response



# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask a question"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response from RAG system
    with st.spinner("Searching and generating response..."):
        response = perform_rag(prompt)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
