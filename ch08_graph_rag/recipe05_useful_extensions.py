"""Recipe 07: Useful extensions for your Graph RAG systems.

This script demonstrates optional enhancements to improve retrieval quality:
1. Add clause summaries
2. Create embeddings for entire SLAs
3. Add supplier-level scores
4. Add domain ontologies
5. Precompute retrieval shortcuts

Environment variables required (placed in .env):
NEO4J_URI=neo4j://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
OPENAI_API_KEY=your_openai_api_key

Run:
python recipe07_useful_extensions.py

pip install python-dotenv neo4j openai
"""

import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
from openai import OpenAI

load_dotenv()


def get_driver():
    uri = os.getenv("NEO4J_URI", "neo4j://localhost:7687")
    user = os.getenv("NEO4J_USERNAME", "neo4j")
    pwd = os.getenv("NEO4J_PASSWORD")
    return GraphDatabase.driver(uri, auth=(user, pwd))


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def create_embedding(text):
    """Generate embeddings using OpenAI's text-embedding-3-small model."""
    response = client.embeddings.create(model="text-embedding-3-small", input=text)
    return response.data[0].embedding


## tag::add_clause_summaries[]
def summarize_clause(text):
    prompt = f"Summarize this SLA clause:\n\n{text}"
    return (
        client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=120,
        )
        .choices[0]
        .message.content
    )


def add_clause_summaries():
    driver = get_driver()
    with driver.session() as session:
        result = session.run(
            "MATCH (cl:Clause) WHERE cl.summary IS NULL RETURN cl.id AS id, cl.text AS text"
        )
        for row in result:
            s = summarize_clause(row["text"])
            session.run(
                "MATCH (cl:Clause {id:$id}) SET cl.summary=$s", id=row["id"], s=s
            )
    driver.close()
    print("✓ Added clause summaries")


add_clause_summaries()
## end::add_clause_summaries[]


## tag::add_sla_embeddings[]
def add_sla_embeddings():
    driver = get_driver()
    with driver.session() as session:
        result = session.run(
            """
            MATCH (s:SLA)-[:HAS_CLAUSE]->(cl:Clause)
            WITH s, collect(cl.text) AS parts
            RETURN s.id AS id, apoc.text.join(parts, '\n') AS full_text
            """
        )
        for r in result:
            emb = create_embedding(r["full_text"])
            session.run(
                "MATCH (s:SLA {id:$id}) SET s.embedding=$emb", id=r["id"], emb=emb
            )
    driver.close()


add_sla_embeddings()
## end::add_sla_embeddings[]


## tag::add_supplier_scores[]
def add_supplier_scores():
    """Add risk scores or other metrics to Company nodes."""
    driver = get_driver()
    with driver.session() as session:
        # Example: Set a risk score for a specific supplier
        session.run(
            """
            MATCH (c:Company {supplier_id: 'SUP123'})
            SET c.risk_score = 0.78
            """
        )
    driver.close()


add_supplier_scores()
## end::add_supplier_scores[]


## tag::add_domain_ontologies[]
def add_domain_ontologies():
    """Connect clause types to standard domain ontologies."""
    driver = get_driver()
    with driver.session() as session:
        session.run(
            """
            MERGE (t:OntologyTerm {name: 'Availability'})
            """
        )
        session.run(
            """
            MATCH (c:ClauseType {name: 'Availability'})
            MATCH (t:OntologyTerm {name: 'Availability'})
            MERGE (c)-[:ALIGNED_WITH]->(t)
            """
        )
    driver.close()


add_domain_ontologies()
## end::add_domain_ontologies[]


## tag::precompute_retrieval_shortcuts[]
def precompute_retrieval_shortcuts():
    """Precompute useful aggregates for faster queries."""
    driver = get_driver()
    with driver.session() as session:
        # Count clauses by type for each company
        session.run(
            """
            MATCH (c:Company)-[:HAS_SLA]->(:SLA)-[:HAS_CLAUSE]->(cl:Clause)-[:OF_TYPE]->(t:ClauseType)
            WITH c, t, count(cl) AS num_clauses
            SET c[t.name + '_count'] = num_clauses
            """
        )
    driver.close()


precompute_retrieval_shortcuts()
## end::precompute_retrieval_shortcuts[]


def create_sla_vector_index():
    """Create a vector index for SLA embeddings (similar to clause embeddings)."""
    driver = get_driver()
    with driver.session() as session:
        try:
            session.run(
                """
                CREATE VECTOR INDEX sla_embeddings IF NOT EXISTS
                FOR (s:SLA)
                ON s.embedding
                OPTIONS {indexConfig: {
                  `vector.dimensions`: 1536,
                  `vector.similarity_function`: 'cosine'
                }}
                """
            )
            print("✓ Created SLA vector index")
        except Exception as e:
            print(f"Note: Vector index may already exist or APOC may be needed: {e}")
    driver.close()


create_sla_vector_index()
