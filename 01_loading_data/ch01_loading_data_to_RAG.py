#!/usr/bin/env python
# coding: utf-8

# ### Required Python Packages
# 
# This notebook uses the following Python packages:
# 
# - `python-docx` (Word document reading)
# - `unstructured` (document partitioning)
# - `python-magic-bin` (file type detection)
# - `pandas` (data manipulation)
# - `PyPDF2` (PDF reading)
# - `pillow` (image processing)
# - `openpyxl` (Excel file reading)
# - `pdf2image` (PDF to image conversion)
# - `pytesseract` (OCR)
# - `openai` (OpenAI API)
# - `python-dotenv` (environment variable management)
# - `sqlalchemy` (database connection)
# - `psycopg2-binary` (PostgreSQL driver)
# - `moviepy` (video processing)
# - `pdfminer.six` (PDF text extraction)
# - `pi-heif` (HEIF image support)
# - `unstructured-inference` (document inference)
# 
# Some helper functions may require additional dependencies. Install these packages using pip before running the notebook.

# In[19]:


get_ipython().system('pip install python-docx==1.1.2')
get_ipython().system('pip install unstructured==0.17.2')
get_ipython().system('pip install python-magic-bin==0.4.14')
get_ipython().system('pip install pandas==2.2.3')
get_ipython().system('pip install PyPDF2==3.0.1')
get_ipython().system('pip install pillow==11.2.1')
get_ipython().system('pip install openpyxl==3.1.5')
get_ipython().system('pip install pdf2image==1.17.0')
get_ipython().system('pip install pytesseract==0.3.13')
get_ipython().system('pip install openai==1.82.1')
get_ipython().system('pip install python-dotenv==1.1.0')
get_ipython().system('pip install sqlalchemy==2.0.41')
get_ipython().system('pip install psycopg2-binary==2.9.10')
get_ipython().system('pip install moviepy==2.2.1')
get_ipython().system('pip install pdfminer.six==20250506')
get_ipython().system('pip install pi-heif==0.22.0')
get_ipython().system('pip install unstructured-inference==1.0.2')


# ### 1.1 Loading Word Files in Python

# Option 1: load word files using the python_docx library

# In[1]:


# tag::python_docx[]
import os
from docx import Document

file_path = "../datasets/word_files/2023_Jan_7_Feature_Engineering_Techniques.docx"

doc = Document(file_path)

text = []
for paragraph in doc.paragraphs:
    text.append(paragraph.text)

full_text = "\n".join(text)
# end::python_docx[]


# In[5]:


full_text


# Option 2: load word files using the unstructured library

# In[ ]:


# tag::unstructured[]
from unstructured.partition.docx import partition_docx
import os
import pandas as pd

elements = partition_docx(filename=file_path)

list_of_elements = []

for element in elements:
    element_dict = {
        "element_id": element.id,
        "file_path": file_path,
        "category": element.category,  # e.g. "Title", "NarrativeText", "ListItem"
        "text": element.text,
        "last_modified": element.metadata.last_modified,
    }

    list_of_elements.append(element_dict)

elements_df = pd.DataFrame(list_of_elements)
# end::unstructured[]


# In[7]:


elements_df.head()


# ### 1.2 Loading PDF Files

# In[8]:


# tag::load_pdf_using_PyPDF2[]
import PyPDF2
import os
import pandas as pd

file_path = "../datasets/pdf_files/2023_Jan_7_Feature_Engineering_Techniques.pdf"

with open(file_path, "rb") as file:
    reader = PyPDF2.PdfReader(file)

    # Initialize an empty string to store the extracted text
    list_of_pages = []
    page_counter = 1

    for page in reader.pages:
        page_dict = {
            "file_name": reader.metadata.get("/Title"),
            "producer": reader.metadata.get("/Producer"),
            "page_number": page_counter,
            "text": page.extract_text(),
            "images": page.images,
        }

        list_of_pages.append(page_dict)

        page_counter += 1
# end::load_pdf_using_PyPDF2[]

# Convert the list of pages to a pandas DataFrame
pages_df = pd.DataFrame(list_of_pages)


# In[9]:


# Display the first few rows of the DataFrame
pages_df.head()


# ### 1.3 Loading and Handling CSV and Excel Files

# In[9]:


row.columns


# In[10]:


###########################################################################################################
# Define the file path to the Word document
###########################################################################################################
# tag::create_additional_table_column[]
import os
import pandas as pd

file_path = "../datasets/csv_files/census-income.xlsx"
df_excel = pd.read_excel(io=file_path)


def create_text_description_of_row(row):
    row["text_description"] = (
        f"""The candidate {row['age']} years old is working in the
            {row['workclass']} sector. The candidate was born in
            {row['native-country']}, is {row['marital-status']}
            and has a {row['relationship']} relationship.
            The candidate has a {row['education']} degree 
            and is working as a {row['occupation']}.
            The income of the candidate is {row['income']}."""
    )

    return row


# Apply the function create_text_description_of_row to each row of the data frame
df_extended = df_excel.apply(create_text_description_of_row, axis=1)
# end::create_additional_table_column[]


# In[11]:


# Display the first 5 text_description of the dataset
df_extended["text_description"].head()


# In[6]:


df_extended["text_description"][0]


# ### 1.4 Querying a PostgreSQL Database

# ```
# CREATE USER rag_user WITH PASSWORD 'raguserpassword123';
# GRANT ALL ON ALL TABLES IN SCHEMA public TO rag_user;
# ```

# In[12]:


from dotenv import load_dotenv

load_dotenv()

################################################################################
# Querying the postgres database using SQLAlchemy
################################################################################


username = os.getenv("POSTGRESQL_USER")  # Your PostgreSQL username
password = os.getenv("POSTGRESQL_PASSWORD")  # Your PostgreSQL password
host = os.getenv("DB_HOST", "localhost")  # Default to localhost if not provided
port = os.getenv("DB_PORT", "5432")  # Default to 5432 if not provided
database = os.getenv("DB_NAME", "postgres")  # Database name (e.g., postgres)

# tag::query_postgres[]
import os
import pandas as pd
from sqlalchemy import create_engine

connection_string = (
    f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"
)
engine = create_engine(connection_string)

with engine.connect() as connection:
    query = """SELECT * FROM categories ORDER BY category_id ASC """
    result = pd.read_sql(query, connection)
    print(result)
# end::query_postgres[]


# ### 1.5 Loading Audio Files by Using Speech-to-Text Models

# In[20]:


from dotenv import load_dotenv
import os
import openai

# Set OPENAI_API_KEY environment variable using the value from the .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# tag::transform_audio_to_text[]
import os
import openai

audio_file_path = "../datasets/audio_files/harvard.wav"

# initialize the OpenAI client with your API key
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

with open(audio_file_path, "rb") as audio_file:
    transcription = client.audio.transcriptions.create(
        model="whisper-1", file=audio_file
    )
# end::transform_audio_to_text[]


# In[21]:


transcription


# ### 1.6 Extracting Text from Images and PDFs Using OCR

# In[1]:


# tag::extract_text_from_financial_reporting_slide_tesseract[]
import os
from pdf2image import convert_from_path
from PIL import Image
import pytesseract

# Load the sample .png file
image = Image.open(fp="../datasets/images/example_finance_reporting_slide.png")

# Use Tesseracst to do OCR on the image
text = pytesseract.image_to_string(image)
# end::extract_text_from_financial_reporting_slide_tesseract[]

###########################################################################################################
# Define the file path to the Word document
###########################################################################################################
# tag::extract_text_from_images[]
import os
from pdf2image import convert_from_path
from PIL import Image
import pytesseract

file_path = "../datasets/images/2023_Jan_7_Feature_Engineering_Techniques.pdf"

# Convert PDF to a list of images
images = convert_from_path(pdf_path=file_path)

text = []
for i, image in enumerate(images):
    page_text = pytesseract.image_to_string(image)
    text.append(page_text)
# end::extract_text_from_images[]


# ### 1.7 Extracting Text from Images using Multimodal Models

# In[4]:


from dotenv import load_dotenv

# Set OPENAI_API_KEY environment variable using the value from the .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# tag::extract_text_from_financial_reporting_slide[]
import os
from PIL import Image
import base64
import openai

png_file_path = "../datasets/images/example_finance_reporting_slide.png"

with open(png_file_path, "rb") as image_file:
    base64_image = base64.b64encode(image_file.read()).decode("utf-8")

    prompt = (
        "Extract the text from the image attached. Make sure to only "
        "extract only the text. If there is no text in the image, "
        "please return with the sentence 'No text found in the image."
    )

    response = openai.chat.completions.create(
        model="gpt-4o",  # define the model to use
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    },
                ],
            }
        ],
        max_tokens=500,
    )

    content = response.choices[0].message.content
# end::extract_text_from_financial_reporting_slide[]


# ### 1.8 Generating Text Summaries for Images Using Multimodal Models

# In[5]:


# Load the environment variables from the .env file
from dotenv import load_dotenv

load_dotenv()

# tag::generate_text_summaries_for_images[]
import base64
import openai

image_path = "../datasets/images/vietnam.png"

with open(image_path, "rb") as image_file:
    base64_image = base64.b64encode(image_file.read()).decode("utf-8")

    prompt = (
        "You are an assistant for visually impaired users. "
        "Describe the image in detail."
    )

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    },
                ],
            }
        ],
        max_tokens=150,
    )

    content = response.choices[0].message.content
# end::generate_text_summaries_for_images[]


# In[6]:


content


# ### 1.9 Generating Text Summaries for Embedded Tables Using Multimodal Models

# In[1]:


# tag::extract_embedded_tables_from_pdf[]
import os
from unstructured.partition.pdf import partition_pdf

pdf_file_path = "../datasets/pdf_files/adult_data_article.pdf"

tables = []
texts = []

# partition the PDF file into its elements
raw_pdf_elements = partition_pdf(
    filename=pdf_file_path,
    strategy="hi_res",
)

for element in raw_pdf_elements:
    if "unstructured.documents.elements.Table" in str(type(element)):
        tables.append(str(element))

# end::extract_embedded_tables_from_pdf[]

# tag::summarize_tables[]
from openai import OpenAI
import pandas as pd


def summarize_tables(row):
    summary_prompt = f"""You are an assistant tasked with summarizing tables. \
                    Give a concise summary of the table. Table chunk: {row.table}"""

    # Initialize the OpenAI API client and generate the table summary
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": summary_prompt}],
        temperature=0.7,
        max_tokens=150,
    )

    row["table_summary"] = response.choices[0].message.content

    return row


# create a pandas dataframe from the tables
tables_df = pd.DataFrame(tables, columns=["table"])

# add a column to the dataframe to store the summaries
tables_df = tables_df.apply(summarize_tables, axis=1)
# end::summarize_tables[]


# In[ ]:


tables_df


# In[ ]:


# tag::test_ask_a_question[]
# define a random question to the embedded table
user_question = "What are the education levels of the people working in Sales?"


def build_prompt_and_generate_answer(user_question, found_table):
    """
    This function builds a prompt using the user's question and the context of the table
    and generates an answer using the OpenAI API

    Parameters:
        user_question: the question asked by the user
        found_table: the table context to generate the answer from

    Returns:
        answered_question: the answer to the user's question
    """

    question_prompt = f"""You are an assistant using the content from PDFs \
                        to answer questions. Below you can find the \
                        user's question and relevant context. Please use the \
                        context to generate an answer to the user's question.

                        # User question: {user_question}

                        # Context: 

                        ## Table summary: 
                        {found_table.table_summary}

                        ## Table content: 
                        {found_table.table}""".stripe()

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    answered_question = (
        client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": question_prompt}],
            temperature=0.7,
            max_tokens=150,
        )
        .choices[0]
        .message.content
    )

    return answered_question


# generate the answer to the user's question
# as context we using the first entry in the tables_df
answered_question = build_prompt_and_generate_answer(
    user_question=user_question, found_table=tables_df.iloc[0]
)

print(answered_question)
# end::test_ask_a_question[]


# ### 1.10 Parsing PDFs with Multiple Media Content Using Unstructured and Multimodal Models

# In[2]:


# tag::extract_pdf_elements[]
from unstructured.partition.pdf import partition_pdf
import os

# set the OCR agent to tesseract
os.environ["OCR_AGENT"] = "tesseract"

pdf_file_path = "../datasets/pdf_files/adult_data_article.pdf"
image_output_dir = "../datasets/extracted_content_from_pdfs/images"

# get elements using the function extract_pdf_elements
raw_pdf_elements = partition_pdf(
    filename=pdf_file_path,
    extract_images_in_pdf=True,
    extract_image_block_types=["Image", "Table"],
    extract_image_block_to_payload=False,
    extract_image_block_output_dir=image_output_dir,
)

# categorize elements by type
tables = []
texts = []
titles = []

# fill the just created lists with the elements
for element in raw_pdf_elements:
    if "unstructured.documents.elements.Table" in str(type(element)):
        tables.append(str(element))
    elif "unstructured.documents.elements.NarrativeText" in str(type(element)):
        texts.append(str(element))
    elif "unstructured.documents.elements.Title" in str(type(element)):
        titles.append(str(element))
# end::extract_pdf_elements[]


# ### 1.11 Loading Videos Using Speech-to-Text and Multimodal Models

# You can find the test video I used on YouTube: [Learn Data Science Tutorial - Full Course for Beginners](https://www.youtube.com/watch?v=ua-CiDNNj30)

# In[ ]:


# tag::load_video_and_extract_frames[]
import os
import pandas as pd

from moviepy import VideoFileClip, TextClip, CompositeVideoClip

video_file_path = "../datasets/videos/learn-data-science-tutorial.mp4"
image_output_folder = "../datasets/videos/video_extracted_images"

clip = VideoFileClip(video_file_path)

# create a list of timestamps from which we want to extract a frame
time_step = 10  # time in seconds
timestamps = list(range(0, int(clip.duration) - time_step, time_step))

# for each timestamp extract a frame
for timestamp in timestamps:
    frame_image_path = os.path.join(image_output_folder, f"frame_{timestamp}.png")
    clip.save_frame(frame_image_path, t=timestamp)
# end::load_video_and_extract_frames[]


# In[ ]:


# tag::video_to_audio[]
# for each timestamp extract the audio sequence and save it to a .mp3 file
audio_output_folder = "../datasets/videos/video_extracted_audio"

for timestamp in timestamps:
    audio_clip = clip.subclip(timestamp, timestamp + time_step).audio
    output_audio_path = os.path.join(audio_output_folder, f"audio_{timestamp}.mp3")
    audio_clip.write_audiofile(output_audio_path)

# end::video_to_audio[]


# In[23]:


# tag::audio_to_text[]
from openai import OpenAI


def audio_to_text(audio_path):
    """
    Convert audio to text using OpenAI's Whisper model.

    Parameters:
    audio_path (str): The path to the audio file.

    Returns:
    str: The text recognized from the audio.

    """
    # Initialize the OpenAI client with your API key

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Open and read the audio file
    with open(audio_path, "rb") as audio_file:
        # Transcribe
        transcription = client.audio.transcriptions.create(
            model="whisper-1", file=audio_file
        )

    # save the transcription to a text file
    text_file_path = audio_path.replace(".mp3", ".txt")
    with open(text_file_path, "w") as text_file:
        text_file.write(transcription.text)

    return


# List all files in folder audio_output_folder
audio_files = os.listdir(audio_output_folder)

for audio_file in audio_files:
    absolut_path_audio_file = os.path.join(audio_output_folder, audio_file)
    # Use the function audio_to_text to convert the audio to text
    audio_to_text(audio_path=absolut_path_audio_file)
# end::audio_to_text[]

