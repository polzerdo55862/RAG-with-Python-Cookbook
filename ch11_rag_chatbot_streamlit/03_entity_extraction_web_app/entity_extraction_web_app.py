import streamlit as st
import openai
import base64
from io import BytesIO
from pydantic import BaseModel, Field
from typing import Optional, List
import re


from pdf2image import convert_from_bytes


def convert_pdf_to_images(pdf_file):
    # Read the PDF file and convert each page to an image
    # (PIL Image objects)
    images = convert_from_bytes(pdf_file.read())

    # Save each image to a temporary PNG file and return the file paths
    image_paths = []
    for idx, image in enumerate(images):
        temp_path = f"images/temp_page_{idx}.png"
        image.save(temp_path, "PNG")
        image_paths.append(temp_path)
    return image_paths



import openai
import base64
from io import BytesIO


def perform_ocr_and_extract_entities(image_paths):
    extracted_text = []

    # Prepare the system message for GPT-4o vision
    system_message = {
        "role": "system",
        "content": (
            "You are an OCR assistant. Extract all text from the "
            "provided images. Do not summarize or skip any content."
        ),
    }

    for image_path in image_paths:
        with open(image_path, "rb") as image_file:
            # Read image data and base64 encode it
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")

        # Create the image_url dictionary directly from the base64 string
        image_content = {
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{base64_image}"},
        }

        messages = [
            system_message,
            {
                "role": "user",
                "content": [image_content],
            },
        ]

        response = openai.chat.completions.create(
            model="gpt-4o", messages=messages, max_tokens=4096
        )

        full_text = response.choices[0].message.content
        extracted_text.append(full_text)

    return extracted_text



from pydantic import BaseModel, Field
from typing import List
import json

def extract_entities_from_text(extracted_text):
    system_message = (
        "Extract all people entities from the text as a JSON array "
        "of objects with fields: ID (int), Name (str), Age (int), "
        "City (str)."
    )
    text = "\n".join(extracted_text)
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": text},
        ],
        max_tokens=1024,
    )
    extracted_data = response.choices[0].message.content

    return extracted_data

st.title("Chat with File Upload")

uploaded_file = st.file_uploader(
    "Upload a PDF file to extract entities",
    type=["pdf"],
)

if uploaded_file:
    with st.spinner("Processing PDF..."):
        if uploaded_file.type == "application/pdf":
            images = convert_pdf_to_images(uploaded_file)
            extracted_text = perform_ocr_and_extract_entities(images)

            st.write("Extracted Text from PDF Pages:")
            for idx, page_text in enumerate(extracted_text, 1):
                st.markdown(f"**Page {idx}:**")
                st.write(page_text)

            extracted_data = extract_entities_from_text(extracted_text)
            st.write("Extracted Entities:")
            st.write(extracted_data)
