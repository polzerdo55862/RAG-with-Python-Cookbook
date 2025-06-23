#!/usr/bin/env python
# coding: utf-8

# In[78]:


get_ipython().system('pip install psycopg2-binary')
get_ipython().system('pip install faiss-cpu')
get_ipython().system('pip install openai')
get_ipython().system('pip install chromadb')
get_ipython().system('pip install pandas')


# ### 4.1 Storing and Working with Embedding using FAISS

# In[79]:


def store_data_to_FAISS():
    # tag::store_data_to_FAISS[]
    import faiss
    import numpy as np
    from openai import OpenAI

    # Example list of sample strings
    text_chunks = [
        "The sky is blue.",
        "The sun is shining.",
        "I love chocolate.",
        "Ice cream is delicious.",
        "Roses are red.",
        "Violets are blue.",
    ]

    # Initialize the OpenAI embeddings model
    client = OpenAI()
    model = "text-embedding-3-small"

    # Generate embeddings for the sample strings
    def get_embedding(text):
        response = client.embeddings.create(input=text, model=model)
        return response.data[0].embedding

    document_embeddings = np.array(
        [get_embedding(text) for text in text_chunks]
    )

    # Convert embeddings to float32 (FAISS requires float32 type)
    document_embeddings = document_embeddings.astype("float32")

    # Create a FAISS index (using L2 distance)
    index = faiss.IndexFlatL2(document_embeddings.shape[1])

    # Add embeddings to the index
    index.add(document_embeddings)
    # end::store_data_to_FAISS[]

    # tag::search_using_FAISS[]
    # generate a query embedding for the user query
    query = "What color do Violets have?"
    query_embedding = np.array(get_embedding(query)).astype("float32")

    # Perform the search: k = number of closest documents you want to retrieve
    k = 5   
    distances, indices = index.search(query_embedding.reshape(1, -1), k)

    # Retrieve the documents corresponding to the indices
    retrieved_documents = [text_chunks[i] for i in indices[0]]
    # end::search_using_FAISS[]

    return distances, indices, retrieved_documents

distances, indices, retrieved_documents = store_data_to_FAISS()


# In[80]:


print("Distances: ", distances)
print("Indices: ", indices)
print("Retrieved document: ", retrieved_documents)


# #### Storing and Working with Embeddings in a PostgreSQL database
# 

# In[81]:


def embeddings_to_chroma_db():
    # tag::create_chroma_client[]
    import chromadb

    # vector store settings
    VECTOR_STORE_PATH = r"../02_Data/00_Vector_Store"
    COLLECTION_NAME = "my_collection"

    # get/create a chroma client and collection
    chroma_client = chromadb.PersistentClient(path=VECTOR_STORE_PATH)
    collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)
    # end::create_chroma_client[]
    # tag::add_text_documents_to_chroma_collection[]
    from openai import OpenAI

    text_chunks = [
        "The sky is blue.",
        "The sun is shining.",
        "I love chocolate.",
        "Ice cream is delicious.",
        "Roses are red.",
        "Violets are blue.",
    ]

    # Generate embeddings
    client = OpenAI()
    model = "text-embedding-3-small"
    def get_embedding(text):
        response = client.embeddings.create(input=text, model=model)
        return response.data[0].embedding

    embeddings_model = client  # for compatibility with later code
    embeddings_list = [get_embedding(text) for text in text_chunks]

    # add data frame to collection
    collection.add(
        embeddings=embeddings_list,
        documents=text_chunks,
        ids=[
            str(i) for i in range(len(text_chunks))
        ],  # create a list of strings as index
    )
    # end::add_text_documents_to_chroma_collection[]

    # tag::query_chroma_db_collection[]
    # query collection
    query = "What is the color of the sky?"
    query_embedding = get_embedding(query)
    results = collection.query(query_embeddings=[query_embedding], n_results=3)
    # end::query_chroma_db_collection[]

    return results

results = embeddings_to_chroma_db()


# In[82]:


results


# #### 4.2 Storing and Working with Embeddings in a PostgreSQL database
# 

# In[83]:


def create_postgres_table():
    """
    This function is used in chapter 4 as a example how to create a table in postgres
    and write vectors to it.

    Used in: 02_write_data_to_postgres.py
    """
    # tag::create_table_and_write_vectors_to_postgres[]
    import psycopg2
    from psycopg2 import Error

    conn = psycopg2.connect(
        dbname="rag_cookbook",
        user="rag_cookbook_user",
        password="rag_cookbook_user_pw",
        host="localhost",
        port="5432",
    )

    cur = conn.cursor()

    # creates the vector extension if it does not exist
    cur.execute("""CREATE EXTENSION IF NOT EXISTS vector""")

    # execute the query to create the table including the vector column
    cur.execute(
        """CREATE TABLE IF NOT EXISTS embeddings_table(
            id integer PRIMARY KEY,
            text_chunk TEXT,
            embedding vector(1536)
        )"""
    )

    conn.commit()
    # end::create_table_and_write_vectors_to_postgres[]

    return conn

conn = create_postgres_table()


# In[84]:


conn


# In[85]:


def write_vectors_to_postgres(conn):
    from openai import OpenAI

    # Define text chunks
    text_chunks = [
        "The sky is blue.",
        "The sun is shining.",
        "I love chocolate.",
        "Ice cream is delicious.",
        "Roses are red.",
        "Violets are blue.",
    ]

    client = OpenAI()
    model = "text-embedding-3-small"

    def get_embedding(text):
        response = client.embeddings.create(input=text, model=model)
        return response.data[0].embedding

    index = 0
    cur = conn.cursor()

    # Insert the embeddings into the table
    for text_chunk in text_chunks:
        embedding = get_embedding(text_chunk)
        cur.execute(
            "INSERT INTO embeddings_table (id, text_chunk, embedding) VALUES (%s, %s, %s)",
            (index, text_chunk, embedding),
        )
        index += 1
    return


# In[86]:


write_vectors_to_postgres(conn)


# Query all data from table embeddings

# In[ ]:


cur = conn.cursor()
cur.execute("SELECT * FROM embeddings_table")
rows = cur.fetchall()   

for row in rows:
    print(row)


# #### Perform similarity search on top of the just create PostgreSQL table

# In[ ]:


def cosine_similarity_search_postgres(conn):
    """
    Perform a cosine similarity search in the PostgreSQL database using OpenAI embeddings.
    Retrieves the top 20 most similar text chunks based on cosine similarity of their embeddings.

    :param conn: psycopg2 connection object to the PostgreSQL database
    :return: List of tuples with cosine similarity and text chunks
    """
    # tag::cosine_similarity_search_postgres[]
    from openai import OpenAI

    # Initialize the OpenAI embeddings model
    client = OpenAI()
    model = "text-embedding-3-small"

    # Example text chunk
    text_chunk = "Sweets are delicious."

    # Get the embedding
    response = client.embeddings.create(input=text_chunk, model=model)
    embeded_query = response.data[0].embedding

    cur = conn.cursor()
    cur.execute(
        f"""
        SELECT 1 - (embedding <=> '{embeded_query}') AS cosine_similarity, *
        FROM embeddings_table
        ORDER BY 1 - (embedding <=> '{embeded_query}') DESC
        LIMIT 20;
    """
    )

    results = cur.fetchall()
    # end::cosine_similarity_search_postgres[]
    conn.commit()

    return results

results = cosine_similarity_search_postgres(conn)


# In[ ]:


results


# ### Write a larger amount of data to the vector store
# 
# For this example we are using the job description dataset to write it to the database.

# In[ ]:


import psycopg2
from psycopg2 import Error

conn = psycopg2.connect(
    dbname="rag_cookbook",
    user="rag_cookbook_user",
    password="rag_cookbook_user_pw",
    host="localhost",
    port="5432",
)

cur = conn.cursor()

# creates the vector extension if it does not exist
cur.execute("""CREATE EXTENSION IF NOT EXISTS vector""")


# execute the query to create the table including the vector column
cur.execute(
    """
    CREATE TABLE IF NOT EXISTS job_description_table(
        id integer PRIMARY KEY,
        text_chunk TEXT,
        embedding vector(1536)
    )
    """
)
conn.commit()


# In[90]:


def fill_postgres_with_job_description():
    import psycopg2
    from psycopg2 import Error
    import pandas as pd

    conn = psycopg2.connect(
        dbname="rag_cookbook",
        user="rag_cookbook_user",
        password="rag_cookbook_user_pw",
        host="localhost",
        port="5432",
    )

    cur = conn.cursor()

    # tag::create_job_description_table[]
    # execute the query to create the table including the vector column
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS job_description_table(
            id integer PRIMARY KEY,
            text_chunk TEXT,
            embedding vector(1536)
        )
        """
    )
    # end::create_job_description_table[]
    conn.commit()
    from openai import OpenAI

    file_path = "../datasets/large_text_dataset/resume_job_description_data.csv"
    df = pd.read_csv(file_path)
    text_chunks = df["job_description_text"]
    print(len(text_chunks))

    try:
        # get all entries from the table
        cur.execute("SELECT * FROM job_description_table")
        rows = cur.fetchall()
        df_from_database = pd.DataFrame(
            rows, columns=["column1", "text_chunks", "column3"]
        )
        text_chunks_existing = df_from_database["text_chunks"]

        # compare text_chunks and text_chunks_existing and only keep the ones which are not already in the table
        text_chunks = [
            text_chunk
            for text_chunk in text_chunks
            if text_chunk not in text_chunks_existing
        ]

    except:
        pass

    client = OpenAI()
    model = "text-embedding-3-small"

    print(len(text_chunks))
    # Insert the embeddings into the table using OpenAI API
    for text_chunk in text_chunks:
        print(text_chunk)
        response = client.embeddings.create(input=text_chunk, model=model)
        embedding = response.data[0].embedding

        # assign a new id to the text chunk
        cur.execute("SELECT MAX(id) FROM job_description_table")
        max_id = cur.fetchone()[0]
        index = max_id + 1 if max_id else 1

        # Insert the id, content, and embedding into the table
        cur.execute(
            "INSERT INTO job_description_table (id, text_chunk, embedding) VALUES (%s, %s, %s)",
            (index, text_chunk, embedding),
        )
        conn.commit()
        print(index)


# In[91]:


results = fill_postgres_with_job_description()


# ### Perform query using HNSW and IVFLL index

# In[ ]:


def perform_hnsw_similarity_search():
    import psycopg2
    from psycopg2 import Error

    conn = psycopg2.connect(
        dbname="rag_cookbook",
        user="rag_cookbook_user",
        password="rag_cookbook_user_pw",
        host="localhost",
        port="5432",
    )

    cur = conn.cursor()
    # tag::perform_ivfflat_similarity_search[]
    from openai import OpenAI

    # generate embedding vector to an example query regarding jobs
    query = "I am looking for a job as a data scientist in Berlin."
    client = OpenAI()
    model = "text-embedding-3-small"
    response = client.embeddings.create(input=query, model=model)
    query_embedding = response.data[0].embedding

    # perform similarity search
    ivfflat_sql = f"""
        DROP TABLE IF EXISTS test_embedding_table;
        CREATE TABLE test_embedding_table AS SELECT * FROM job_description_table;
        CREATE INDEX ON test_embedding_table USING ivfflat (embedding vector_cosine_ops) 
        WITH (lists = 30);  -- Increase the number of lists for faster search
        SET ivfflat.probes = 3;  -- Reduce the number of probes for faster search
        EXPLAIN ANALYZE SELECT 1 - (embedding <=> '{str(query_embedding)}') 
        AS cosine_similarity, *
        FROM test_embedding_table
        ORDER BY 1 - (embedding <=> '{str(query_embedding)}') DESC
        LIMIT 20;
        """

    cur.execute(ivfflat_sql)
    ivfflat_search = cur.fetchall()
    # end::perform_ivfflat_similarity_search[]

    # tag::perform_hnsw_similarity_search[]
    hnsw_test_sql = f"""
        DROP TABLE IF EXISTS test_embedding_table;
        CREATE TABLE test_embedding_table AS SELECT * FROM job_description_table;
        CREATE INDEX ON test_embedding_table USING hnsw (embedding vector_cosine_ops) 
        WITH (m = 16, ef_construction = 200);
        SET hnsw.ef_search = 50;
        EXPLAIN ANALYZE SELECT 1 - (embedding <=> '{str(query_embedding)}') 
        AS cosine_similarity, *
        FROM test_embedding_table
        ORDER BY 1 - (embedding <=> '{str(query_embedding)}') DESC
        LIMIT 20;
    """

    cur.execute(hnsw_test_sql)
    hnsw_search = cur.fetchall()
    # end::perform_hnsw_similarity_search[]

    # [..., ('Planning Time: 1.109 ms',), ('Execution Time: 13.927 ms',)]

    # tag::perform_full_search[]
    full_search_sql = f"""
        EXPLAIN ANALYZE SELECT 1 - (embedding <=> '{str(query_embedding)}') 
        AS cosine_similarity,
        * FROM job_description_table
        ORDER BY 1 - (embedding <=> '{str(query_embedding)}') DESC
        LIMIT 20;
        """
    # end::perform_full_search[]
    cur.execute(full_search_sql)

    results_full_search = cur.fetchall()
    # [..., ('Planning Time: 13.669 ms',), ('Execution Time: 85.582 ms',)]
    return ivfflat_search, hnsw_search, results_full_search



# In[ ]:


ivfflat_search, hnsw_search, results_full_search = perform_hnsw_similarity_search()
print(f"Index HSNW search: {hnsw_search[6]}")
print(f"Index IVFFLat search: {ivfflat_search[6]}")
print(f"Full search: {results_full_search[6]}")


# In[ ]:


def duplicate_rows_in_postgres():
    """
    Connect to PostgreSQL, load data from the table job_description_table, and duplicate the rows.
    """
    import psycopg2
    from psycopg2 import Error

    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            dbname="rag_cookbook",
            user="rag_cookbook_user",
            password="rag_cookbook_user_pw",
            host="localhost",
            port="5432",
        )
        cur = conn.cursor()

        # Load data from the table job_description_table
        cur.execute("SELECT * FROM job_description_table")
        rows = cur.fetchall()

        # Get the maximum current ID
        cur.execute("SELECT MAX(id) FROM job_description_table")
        max_id = cur.fetchone()[0]

        # Duplicate the rows with new unique IDs
        for i, row in enumerate(rows):
            cur.execute(
                "INSERT INTO job_description_table (id, text_chunk, embedding) VALUES (%s, %s, %s)",
                (max_id + i + 1, row[1], row[2]),
            )
            print(f"inserted {row[1]}")
        # Commit the transaction
        conn.commit()

    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)

    finally:
        if conn:
            cur.close()
            conn.close()
            print("PostgreSQL connection is closed")


# In[ ]:


duplicate_rows_in_postgres()


# ## Hybrid search using PostgreSQL

# In[92]:


def hybrid_search_postgres():
    import psycopg2
    from psycopg2 import Error

    conn = psycopg2.connect(
        dbname="rag_cookbook",
        user="rag_cookbook_user",
        password="rag_cookbook_user_pw",
        host="localhost",
        port="5432",
    )

    cur = conn.cursor()

    # tag::hybrid_search_postgres[]
    # generate embedding vector to an example query regarding jobs
    from openai import OpenAI

    query = "I am looking for a job as a data scientist in Berlin."
    client = OpenAI()
    model = "text-embedding-3-small"
    response = client.embeddings.create(input=query, model=model)
    query_embedding = response.data[0].embedding

    # perform similarity search
    hybrid_search_table = f"""
        DROP TABLE IF EXISTS test_embedding_table;
        CREATE TABLE test_embedding_table AS 
        SELECT *, to_tsvector(text_chunk) AS tsv 
        FROM job_description_table;
        """

    cur.execute(hybrid_search_table)

    hybrid_search_query = f"""
        WITH ranked_docs AS (
            SELECT 
                id, 
                text_chunk AS text, 
                ts_rank(tsv, plainto_tsquery('PostgreSQL')) AS text_score,  
                1 - (embedding <=> '{str(query_embedding)}') AS vector_score,
                ts_rank(tsv, plainto_tsquery('PostgreSQL')) 
                * 0.5 + (1 - (embedding <=> '{str(query_embedding)}')) * 0.5 
                AS hybrid_score
            FROM test_embedding_table
            WHERE tsv @@ plainto_tsquery('PostgreSQL') -- Filter for relevant text first
            ORDER BY hybrid_score DESC
            LIMIT 10
        )
        SELECT * FROM ranked_docs;
        """

    cur.execute(hybrid_search_query)
    results = cur.fetchall()
    # end::hybrid_search_postgres[]
    return results



# In[93]:


hybrid_search_postgres()

