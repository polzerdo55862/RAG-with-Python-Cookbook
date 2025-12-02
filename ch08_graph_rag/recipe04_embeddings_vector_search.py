"""Recipe 04: Adding embeddings and vector search to the SLA knowledge graph.

Steps:
1. Create clause embeddings
2. Create vector index (approximate nearest neighbor)
3. Pure semantic similarity search
4. Hybrid search by industry filter
"""

from __future__ import annotations
import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from neo4j import GraphDatabase
from openai import OpenAI

load_dotenv()
client = OpenAI()


def get_driver():
    """Create Neo4j driver instance."""
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USERNAME")
    pwd = os.getenv("NEO4J_PASSWORD")
    return GraphDatabase.driver(uri, auth=(user, pwd))


## tag::create_embedding[]
def create_embedding(text):
    """Generate embeddings using OpenAI's text-embedding-3-small model."""
    response = client.embeddings.create(model="text-embedding-3-small", input=text)
    return response.data[0].embedding


def create_clause_embeddings():
    """Add embeddings to all Clause nodes in the graph."""
    driver = get_driver()
    with driver.session() as session:
        result = session.run("MATCH (cl:Clause) RETURN cl.id AS id, cl.text AS text")
        for row in result:
            emb = create_embedding(row["text"])
            session.run(
                "MATCH (cl:Clause {id:$id}) SET cl.embedding=$emb",
                id=row["id"],
                emb=emb,
            )
    driver.close()


## end::create_embedding[]


## tag::create_vector_index[]
def create_vector_index():
    """Create a vector index for semantic search on Clause embeddings."""
    driver = get_driver()
    with driver.session() as session:
        session.run(
            """
            CREATE VECTOR INDEX clause_embeddings IF NOT EXISTS
            FOR (c:Clause) ON c.embedding
            OPTIONS { 
                indexConfig: { 
                    `vector.dimensions`: 1536, 
                    `vector.similarity_function`: "cosine" 
                } 
            }
            """
        )
    driver.close()


create_vector_index()
## end::create_vector_index[]


## tag::semantic_search[]
def semantic_search(query, top_k=5):
    """Find clauses semantically similar to the query."""
    driver = get_driver()
    emb = create_embedding(query)
    cypher = """
    CALL db.index.vector.queryNodes(
        "clause_embeddings", $top_k, $embedding
    )
    YIELD node, score
    RETURN node.title AS title, 
           node.text AS text, 
           score 
    ORDER BY score DESC
    """
    with driver.session() as session:
        rows = [r.data() for r in session.run(cypher, top_k=top_k, embedding=emb)]
    driver.close()
    return rows


semantic_search("What is the uptime guarantee?", top_k=3)
## end::semantic_search[]


## tag::hybrid_search_by_industry[]
def hybrid_search_by_industry(query, industry, top_k=5):
    """Combine semantic search with industry filtering."""
    driver = get_driver()
    emb = create_embedding(query)
    cypher = """
    CALL db.index.vector.queryNodes(
        "clause_embeddings", $top_k, $embedding
    ) 
    YIELD node, score
    MATCH (node)<-[:HAS_CLAUSE]-(s:SLA)<-[:HAS_SLA]-(c:Company)
    WHERE c.industry = $industry
    RETURN c.name AS company, 
           s.id AS sla_id, 
           node.title AS clause_title, 
           node.text AS clause_text, 
           score
    ORDER BY score DESC
    """
    with driver.session() as session:
        rows = [
            r.data()
            for r in session.run(cypher, top_k=top_k, embedding=emb, industry=industry)
        ]
    driver.close()
    return rows


hybrid_search_by_industry(
    query="What are the data privacy obligations?",
    industry="Healthcare",
    top_k=3,
)
## end::hybrid_search_by_industry[]
