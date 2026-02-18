#!/bin/bash

# Set Streamlit server address to allow external connections
# and use the PORT environment variable if available, otherwise default to 8501
streamlit run streamlit_app.py --server.port "${PORT:-8501}" --server.address 0.0.0.0