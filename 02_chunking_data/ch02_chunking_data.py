#!/usr/bin/env python
# coding: utf-8

# ### Required Python Packages
# 
# This notebook uses the following Python packages:
# 
# - `PyPDF2` (PDF reading)
# - `pandas` (data manipulation)
# - `pydantic` (data validation)
# - `openai` (OpenAI API)
# - `matplotlib` (visualization)
# - `scikit-learn` (PCA and ML utilities)
# - `python-docx` (Word document reading)
# - `nltk` (text splitting)
# 
# Some helper functions may require additional dependencies. Install these packages using pip before running the notebook.

# In[87]:


get_ipython().system('pip install PyPDF2==3.0.1')
get_ipython().system('pip install pandas==2.2.3')
get_ipython().system('pip install pydantic==2.11.5')
get_ipython().system('pip install openai==1.83.0')
get_ipython().system('pip install matplotlib==3.10.3')
get_ipython().system('pip install scikit-learn==1.6.1')
get_ipython().system('pip install python-docx==1.1.2')
get_ipython().system('pip install nltk==3.9.1')
get_ipython().system('pip install langchain==0.3.25')
get_ipython().system('pip install langchain_openai==0.3.21')
get_ipython().system('pip install langchain-experimental==0.3.4')


# ### 2.1 Adding Metadata to Enable Metadata Filtering

# In[58]:


def load_pdf_and_metadata():
    """
    Load a PDF file and extract the text and metadata
    Returns:
        text (str): The text content of the PDF
        metadata (dict): The metadata of the PDF
    """

    # tag::load_pdf_and_metadata[]
    import PyPDF2
    import os

    file_path = "../datasets/pdf_files/attention_is_all_you_need_paper.pdf"

    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        metadata = reader.metadata

        text = ""
        for page in reader.pages:
            text += page.extract_text()
    # end::load_pdf_and_metadata[]

    # tag::generate_customized_metadata[]
    metadata = dict(metadata)
    metadata["page_count"] = len(reader.pages)
    metadata["file_size"] = os.path.getsize(file_path)
    metadata["file_name"] = os.path.basename(file_path)
    metadata["file_path"] = file_path
    metadata["text_length"] = len(text)
    # end::generate_customized_metadata[]

    # tag::extract_metadata_from_text_using_LLMs[]
    from pydantic import BaseModel
    from openai import OpenAI

    client = OpenAI()

    class AuthorContact(BaseModel):
        name: str
        company: str
        email: list[str]

    class Contacts(BaseModel):
        entries: list[AuthorContact]

    system_message = """Extract the contact information of all authors."""

    completion = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": system_message,
            },
            {
                "role": "user",
                "content": text,
            },
        ],
        response_format=Contacts,
    )

    author_contacts = completion.choices[0].message.parsed

    metadata["author_contacts"] = author_contacts
    # end::extract_metadata_from_text_using_LLMs[]
    return text, metadata


# load a pdf and all metadata
text, metadata = load_pdf_and_metadata()


# In[59]:


text


# In[63]:


metadata


# ### 2.2 Enhancing Data Quality by Replacing Abbreviations and Technical Terms

# In[6]:


def load_file_and_replace_abbreviations():
    """
    Load a text file and replace abbreviations with their full forms
    Returns:
        text (str): The text content of the file with abbreviations replaced
    """
    # tag::load_file_and_replace_abbreviations[]
    import re

    abbreviations_dict = {
        "NLP": "Natural Language Processing",
        "RNN": "Recurrent Neural Network",
        "LSTM": "Long Short-Term Memory",
        "GRU": "Gated Recurrent Unit",
        "TF": "Transformer",
        "MHA": "Multi-Head Attention",
        "FFN": "Feed-Forward Network",
    }

    # Load the sample text file
    file_path = "../datasets/text_files/blog_post_transformers.txt"
    with open(file_path, "r") as file:
        text = file.read()

    # Replace abbreviations in the text
    for abbr, full_form in abbreviations_dict.items():
        text = re.sub(rf"\b{abbr}\b", f"{full_form} ({abbr})", text)
    # end::load_file_and_replace_abbreviations[]

    return text

# replace abbreviations with full words
processed_text = load_file_and_replace_abbreviations()


# In[ ]:


processed_text


# In[ ]:


def make_text_chunks_self_explanatory():
    # tag::make_text_chunks_self_explanatory[]
    import os
    from openai import OpenAI

    file_path = "../datasets/text_files/EMEA_drives_revenue.txt"

    with open(file_path, "r") as file:
        text = file.read()

    prompt = f"""
        The text below contains a financial report including a lot of abbreviations and
        technical terms from the finance domain. Please replace the abbreviations with
        their full forms and provide a brief explanation of the technical terms, so the 
        whole text get's easier to read and understandable for everyone.

        Make sure it's easy enough, that a 10 years old school kid could understand it.

        Often used abbreviations are:
        - EMEA: Europe, Middle East, and Africa
        - BD: Business Development
        - YoY: Year-over-Year
        - APAC: Asia-Pacific

        Text:
        {text}
        """.strip()

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-4o",
    )

    enhanced_text = chat_completion.choices[0].message.content

    # end::make_text_chunks_self_explanatory[]
    return enhanced_text

enhanced_text = make_text_chunks_self_explanatory()


# In[85]:


# write enhanced_text to a new .txt file
output_file_path = "../datasets/text_files/EMEA_drives_revenue_enhanced.txt"
with open(output_file_path, "w") as file:
    file.write(enhanced_text)


# ### 2.3 Improving Search Accuracy by Embedding Hypothetical Questions

# In[2]:


def load_text_from_sample_chat_history():
    """
    Load text from a sample chat history stored as PDF
    Returns:
        text (str): The text from the sample chat history
    """

    file_path = "../datasets/pdf_files/AI_in_Factories_Discussion_Cleaned.pdf"

    def load_pdf(file_path):
        """
        Load and read a PDF file
        Returns the text content as a string
        """
        with open(file_path, "rb") as file:
            # Create PDF reader object
            reader = PyPDF2.PdfReader(file)

            # Extract text from all pages
            text = ""
            for page in reader.pages:
                text += page.extract_text()

            return text

    # Example usage
    text = load_pdf(file_path=file_path)

    return text


# load pdf with a sample chat history
text = load_text_from_sample_chat_history()


# In[1]:


from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    separators=[
        "\n\n",
    ],
)

# Split the text into smaller chunks
text_chunks = text_splitter.split_text(text)


# In[68]:


def generate_hypothetical_questions(text):
    """
    Generate hypothetical questions from the text
    Args:
        text (str): The text to generate hypothetical questions from
    Returns:
        hypothetical_questions (list): List of hypothetical questions
    """
    # tag::generate_hypothetical_questions[]
    import os
    from openai import OpenAI
    from pydantic import BaseModel
    import textwrap

    file_path = "../datasets/text_files/AI_in_factories_chat.txt"

    with open(file_path, "r") as file:
        text = file.read()

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    prompt = textwrap.dedent(
        f"""
        Below you can find a chat history between two students.

        Please generate 5 hypothetical questions that could be 
        answered using the information from the discussion. 
        The questions should focus on key details, definitions, and 
        information present in the text. 

        Chat History:
        {text}
        """
    )

    class HypotheticalQuestions(BaseModel):
        questions: list[str]

    # generate hypothetical questions using the GPT-4 model
    completion = client.beta.chat.completions.parse(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-4o",
        response_format=HypotheticalQuestions,
    )

    hypothetical_questions = completion.choices[0].message.parsed.questions
    # end::generate_hypothetical_questions[]

    return hypothetical_questions

hypothetical_questions = generate_hypothetical_questions(text)


# In[69]:


hypothetical_questions


# ### 2.4 Splitting Documents Using Character Splitting

# In[48]:


def character_text_splitting():
    """
    Split the text into smaller chunks using the CharacterTextSplitter
    """
    # tag::character_text_splitting[]
    from langchain.text_splitter import CharacterTextSplitter

    file_path = "../datasets/text_files/blog_post_transformers.txt"

    # Load example document
    with open(file_path, "r") as file:
        text = file.read()

    text_splitter = CharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=0,
        separator="",
        length_function=len,
    )

    text_chunks = text_splitter.create_documents([text])
    # end::character_text_splitting[]

    return text_chunks

text_chunks = character_text_splitting()


# In[49]:


text_chunks


# ### 2.5 Splitting Documents Using Recursive Text Splitters

# In[50]:


def recursive_text_splitting():
    """
    Split the text into smaller chunks using the RecursiveCharacterTextSplitter
    """
    # tag::recursive_chunking[]
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    import PyPDF2

    file_path = "../datasets/pdf_files/daily_insights.pdf"

    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)

        text = ""
        for page in reader.pages:
            text += page.extract_text()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=0,
        length_function=len,
        is_separator_regex=False,
    )

    chunks = text_splitter.split_text(text)
    # end::recursive_chunking[]

    return chunks


# load sample pdf and chunk it using recursive character text splitter
text_chunks = recursive_text_splitting()


# In[53]:


print(text_chunks)
print(f"Number of chunks: {len(text_chunks)}")

for chunk in text_chunks:
    print(f"Chunk length: {len(chunk)}")


# ### 2.6 Document Aware Splitting

# In[ ]:


def document_aware_chunking():
    """
    Depending on the file extension, the text is split into chunks using the appropriate text splitter.
    Args:
        file_extension (str): The file extension of the document
    Returns:
        chunks (list): List of text chunks
    """
    # tag::document_aware_text_splitter[]
    import os

    file_path = "../datasets/markdown_files/random_md_code.md"
    file_extension = os.path.splitext(file_path)[1]

    with open(file_path, "r") as file:
        file_text = file.read()

    from langchain_text_splitters import (
        PythonCodeTextSplitter,
        LatexTextSplitter,
        MarkdownHeaderTextSplitter,
    )

    if file_extension == ".py":
        splitter = PythonCodeTextSplitter(chunk_size=500, chunk_overlap=50)
    elif file_extension == ".tex":
        splitter = LatexTextSplitter(chunk_size=500, chunk_overlap=50)
    elif file_extension == ".md":
        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]

        splitter = MarkdownHeaderTextSplitter(headers_to_split_on)

    chunks = splitter.split_text(file_text)
    # end::document_aware_text_splitter[]

    return chunks

text_chunks = document_aware_chunking()


# In[44]:


text_chunks


# ### 2.7 Splitting the Text Using Semantic Aware Chunkers

# In[ ]:


from docx import Document
from openai import OpenAI

file_path = "../datasets/text_files/random-text-about-5-different-stories.txt"

# read the text from the file
with open(file_path, "r") as file:
    text = file.read()


def langchain_semantic_text_splitting(text):
    # tag::langchain_semantic_text_splitting[]
    from langchain_experimental.text_splitter import SemanticChunker
    from langchain_openai.embeddings import OpenAIEmbeddings

    # Define the Semantic Text Splitter
    text_splitter = SemanticChunker(
        OpenAIEmbeddings(),
        breakpoint_threshold_type="percentile",
        breakpoint_threshold_amount=90,
    )

    # Split textchunks
    chunks = text_splitter.split_text(text)
    return 

    # end::langchain_semantic_text_splitting[]

chunks = langchain_semantic_text_splitting(text)


# In[25]:


chunks


# In[26]:


# initialize the api key
client = OpenAI()
embedding_model = "text-embedding-3-small"


def from_text_to_embeddings(chunks, client, embedding_model):
    """
    Translate sentences into vector embeddings

    Attributes:
        - text_chunks (list): list of example strings

    Returns:
        - embeddings_df (DataFrame): data frame with the columns "text_chunk" and "embeddings"
    """
    import os

    # Initialize the OpenAI client with your API key
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # create new data frame using text chunks list
    embeddings_df = pd.DataFrame(text_chunks).rename(columns={0: "text_chunk"})

    # helper function to get the embeddings for a text chunk
    def _get_embeddings(text_chunk, client, embedding_model):
        embedding = (
            client.embeddings.create(input=[text_chunk], model=embedding_model)
            .data[0]
            .embedding
        )

        return embedding

    # iterate over embeddings_df["text_chunks"] and create a new data frame with the embeddings
    embeddings_df["embeddings"] = embeddings_df["text_chunk"].apply(
        _get_embeddings, client=client, embedding_model="text-embedding-3-small"
    )

    # split the embeddings column into individual columns for each vector dimension
    embeddings_df = embeddings_df["embeddings"].apply(pd.Series)
    embeddings_df["text_chunk"] = text_chunks

    return embeddings_df

embeddings_df = from_text_to_embeddings(
    chunks, client, embedding_model
)


# In[29]:


embeddings_df


# ### 2.8 Splitting Text Using Agentic Chunkers

# In[39]:


def agentic_chunking_create_propositions(text):
    """
    Generate propositions from the text
    Args:
        text (str): The text to generate propositions from
    Returns:
        propositions (list): List of propositions
    """

    # tag::agentic_chunking_create_propositions[]
    from langchain import hub
    from langchain_openai import ChatOpenAI  # Import ChatOpenAI
    from pydantic import BaseModel
    from typing import List

    # pull the prompt template from the langchain hub
    obj = hub.pull("wfh/proposal-indexing")

    # define the llm you want to use
    llm = ChatOpenAI(model="gpt-4o")

    # A Pydantic model to extract sentences from the passage
    class Sentences(BaseModel):
        sentences: List[str]

    extraction_llm = llm.with_structured_output(Sentences)

    # Create the sentence extraction chain
    extraction_chain = obj | extraction_llm

    # Test it out
    propositions = extraction_chain.invoke(
        """
        On July 20, 1969, astronaut Neil Armstrong walked on the moon . 
        He was leading the NASA's Apollo 11 mission. 
        Armstrong famously said, "That's one small step for man, one 
        giant leap for mankind" as he stepped onto the lunar surface.
        """
    )

    print(propositions)
    # end::agentic_chunking_create_propositions[]
    return propositions


# In[40]:


# propositions
propositions = agentic_chunking_create_propositions(text)


# In[ ]:


for sentence in propositions.sentences:
    print(sentence)

