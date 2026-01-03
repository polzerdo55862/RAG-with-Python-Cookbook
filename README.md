# RAG-with-Python-Cookbook

| Chapter | Title                             | Colab Notebook Link                                                                                                                                      |
| ------- | --------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1       | RAG Setup                         | https://colab.research.google.com/github/polzerdo55862/RAG-with-Python-Cookbook/blob/main/ch01_RAG_intro/rag_basics.ipynb                                |
| 2       | Generation and Prompt Engineering | https://colab.research.google.com/github/polzerdo55862/RAG-with-Python-Cookbook/blob/main/ch02_generation/generation.ipynb                               |
| 3       | Loading Data                      | https://colab.research.google.com/github/polzerdo55862/RAG-with-Python-Cookbook/blob/main/ch03_loading_data/loading_data_to_RAG.ipynb                    |
| 4       | Data Preparation                  | https://colab.research.google.com/github/polzerdo55862/RAG-with-Python-Cookbook/blob/main/ch04_data_preparation_chunking_data/chunking_data.ipynb        |
| 5       | Embeddings                        | https://colab.research.google.com/github/polzerdo55862/RAG-with-Python-Cookbook/blob/main/ch05_text_embedding/text_embeddings.ipynb                      |
| 6       | Similarity Search                 | https://colab.research.google.com/github/polzerdo55862/RAG-with-Python-Cookbook/blob/main/ch06_similarity_search_vector_databases/vector_databases.ipynb |
| 7       | Retrieval                         | https://colab.research.google.com/github/polzerdo55862/RAG-with-Python-Cookbook/blob/main/ch07_retrieval/retrieval_techniques.ipynb                      |
| 8       | Graph RAG (Overview)              | https://colab.research.google.com/github/polzerdo55862/RAG-with-Python-Cookbook/blob/main/ch08_graph_rag/recipe01_basic_sla_graph.ipynb                  |
| 8.1     | Basic SLA Graph                   | https://colab.research.google.com/github/polzerdo55862/RAG-with-Python-Cookbook/blob/main/ch08_graph_rag/recipe01_basic_sla_graph.ipynb                  |
| 8.2     | Enrich Company Data               | https://colab.research.google.com/github/polzerdo55862/RAG-with-Python-Cookbook/blob/main/ch08_graph_rag/recipe02_enrich_company_data.ipynb              |
| 8.3     | Cypher Queries                    | https://colab.research.google.com/github/polzerdo55862/RAG-with-Python-Cookbook/blob/main/ch08_graph_rag/recipe03_cypher_queries.ipynb                   |
| 8.4     | Embeddings Vector Search          | https://colab.research.google.com/github/polzerdo55862/RAG-with-Python-Cookbook/blob/main/ch08_graph_rag/recipe04_embeddings_vector_search.ipynb         |
| 8.5     | Useful Extensions                 | https://colab.research.google.com/github/polzerdo55862/RAG-with-Python-Cookbook/blob/main/ch08_graph_rag/recipe05_useful_extensions.ipynb                |
| 9       | Agentic RAG                       | -                                                                                                                                                        |
| 10      | RAG Evaluation                    | https://colab.research.google.com/github/polzerdo55862/RAG-with-Python-Cookbook/blob/main/ch10_rag_evaluation/rag_evaluation_techniques.ipynb -          |
| 11      | RAG Chatbot (Streamlit)           | -                                                                                                                                                        |

This repository contains code snippets and practical recipes featured in the O'Reilly book **"RAG with Python Cookbook"**. The book is a comprehensive guide to Retrieval-Augmented Generation (RAG) systems, providing hands-on solutions for building, evaluating, and deploying RAG applications using Python. Each chapter focuses on a specific aspect of RAG, with ready-to-use code and explanations to help you implement state-of-the-art techniques in your own projects.

## What is this book about?

The RAG with Python Cookbook is designed for developers, data scientists, and machine learning practitioners who want to:

- Load and preprocess diverse data types for RAG systems
- Generate and visualize text and image embeddings
- Store and search embeddings using vector databases
- Implement advanced retrieval techniques
- Evaluate RAG systems with human and automated methods
- Build and deploy RAG-powered web applications

## Book Outline

Explore the folders in this repository to find code examples and notebooks for each chapter and recipe. Contributions and feedback are welcome!

### Chapter 1: RAG Setup

[in progress]

### Chapter 2: Generation and Prompt Engineering

[in progress]

### Chapter 3: Loading Data

Colab link: https://colab.research.google.com/github/polzerdo55862/RAG-with-Python-Cookbook/blob/main/ch03_loading_data/loading_data_to_RAG.ipynb

- 3.1 Loading Word Files in Python
- 3.2 Loading PDF Files
- 3.3 Loading and Handling Tabular Data from Excel Files
- 3.4 Loading Structured Data from a PostgreSQL Database
- 3.5 Loading Audio Files Using Speech-to-Text Models
- 3.6 Extracting Text from Images and PDFs Using Tesseract OCR
- 3.7 Extracting Text from Images Using Multimodal Models
- 3.8 Generating Text Description for Images Using Multimodal Models
- 3.9 Generating Text Summaries for Embedded Tables Using Multimodal Models
- 3.10 Parsing PDFs with Multiple Media Content Using Unstructured and Multimodal Models
- 3.11 Loading Videos Using Speech-to-Text and Multimodal Models

### Chapter 4: Data Preparation

Colab link: https://colab.research.google.com/github/polzerdo55862/RAG-with-Python-Cookbook/blob/main/ch04_data_preparation_chunking_data/chunking_data.ipynb

- 4.1 Adding Metadata to Enable Metadata Filtering
- 4.2 Enhancing Data Quality by Replacing Abbreviations and Technical Terms
- 4.3 Improving Search Accuracy by Embedding Hypothetical Questions
- 4.4 Splitting Documents Using Character Splitting
- 4.5 Splitting Documents Using Recursive Text Splitters
- 4.6 Document Aware Splitting
- 4.7 Splitting Text Using Semantic Aware Chunkers
- 4.8 Splitting Text Using Agentic Chunkers

### Chapter 5: Embeddings

Colab link: https://colab.research.google.com/github/polzerdo55862/RAG-with-Python-Cookbook/blob/main/ch05_text_embedding/text_embeddings.ipynb

- 5.1 Mapping Linguistic Meaning of Text Chunks to Numerical Representation
- 5.2 Visualizing Semantic Relationships by Reducing Dimensionality of Embedding Vectors
- 5.3 Calculating Distance Between Embeddings
- 5.4 Choosing the Right Embedding Model
- 5.5 Generating Embeddings for Images and Text Using CLIP
- 5.6 Performing Text Classification Using Embeddings
- 5.7 Improving Search Results Using a Hybrid Search Approach

### Chapter 6: Similarity Search

Colab link: https://colab.research.google.com/github/polzerdo55862/RAG-with-Python-Cookbook/blob/main/ch07_retrieval/retrieval_techniques.ipynb

- 6.1 Choosing the Right Vector Database
- 6.2 Storing and Searching Embeddings Using FAISS
- 6.3 Storing and Working with Embeddings in a Chroma Vector Database
- 6.4 Storing Embeddings in PostgreSQL Using the pgvector Extension
- 6.5 Performing Similarity Search in PostgreSQL
- 6.6 Speeding Up Vector Searches in PostgreSQL Using Indexing Techniques Supported by pgvector
- 6.7 Combining Keyword and Similarity Search for Better Results (Hybrid Search) with PostgreSQL

### Chapter 7: Retrieval

Colab link: https://colab.research.google.com/github/polzerdo55862/RAG-with-Python-Cookbook/blob/main/ch07_retrieval/retrieval_techniques.ipynb

- 7.1 Optimizing Query Results Using Metadata Filtering in PostgreSQL
- 7.2 Enhancing Search Results by Extending the Original Query with Generated Pseudo-Documents
- 7.3 Improving Search Results with Multi-Query Retrieval
- 7.4 Addressing Complex Requests by Designing a Query Routing System
- 7.5 Increasing Search Efficiency by Designing an Auto-Merging Retriever (Parent Document Retriever)
- 7.6 Increasing Search Results by Designing a Sentence Window Retriever
- 7.7 Improving Search Accuracy with Reranking Methods
- 7.8 Decomposing Complex Queries into Multiple Sub-Queries

### Chapter 8: Agentic RAG

[in progress]

### Chapter 9: Graph RAG

[in progress]

### Chapter 10: Evaluation

- 10.1 Evaluating RAG Systems by Humans
- 10.2 Creating Synthetic Data for Automated Testing
- 10.3 Evaluating the Retriever Step by Calculating Context Precision@k
- 10.4 Evaluating RAG Systems Using LLMs as Judge and Faithfulness Metrics
- 10.5 RAG Evaluation Using Response Relevancy

### Chapter 11: RAG Chatbot

- 11.1 Building a Basic Weather Assistant Chatbot
- 11.2 Building a Multimodal PDF Analyzer App
- 11.3 Building a Data Analyst Chatbot Using the Text-to-SQL Approach
- 11.4 Deploying Your Streamlit App Using Docker and AWS
- 11.5 Incorporating Effective User Feedback Functionality
  [in progress]
