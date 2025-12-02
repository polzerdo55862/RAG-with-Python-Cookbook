"""Recipe 01: Creating your first Neo4j knowledge graph for SLA documents.

This file consolidates the steps:
1. Connect to Neo4j
2. Create constraints
3. Parse an SLA Markdown file into Clause objects
4. Infer ClauseType labels
5. Write SLA and Clause nodes (including NEXT and OF_TYPE) into the graph

Environment variables required (placed in .env):
NEO4J_URI=neo4j://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password

Run:
python recipe01_basic_sla_graph.py --sla sample_sla.md --sla-id SLA1 --title "Sample SLA"

pip install python-dotenv neo4j
"""

from __future__ import annotations
import argparse
import os
import re
from dataclasses import dataclass
from typing import List
from dotenv import load_dotenv

load_dotenv()


## tag::code_neo4j_sla_connection[]
from neo4j import GraphDatabase


# create a Neo4j driver instance that you will reuse throughout the script
def get_driver():
    """Create Neo4j driver from environment variables."""
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USERNAME")
    pwd = os.getenv("NEO4J_PASSWORD")
    return GraphDatabase.driver(uri, auth=(user, pwd))


driver = get_driver()
## end::code_neo4j_sla_connection[]


# Here you define and create uniqueness constraints for SLA, Clause, and ClauseType nodes.
# These constraints prevent duplicate nodes and keep your MERGE operations predictable.
## tag::code_neo4j_constraints[]
def create_constraints(driver):
    """Create uniqueness constraints for graph nodes."""
    constraints = [
        "CREATE CONSTRAINT sla_id IF NOT EXISTS " "FOR (s:SLA) REQUIRE s.id IS UNIQUE",
        "CREATE CONSTRAINT clause_id IF NOT EXISTS "
        "FOR (c:Clause) REQUIRE c.id IS UNIQUE",
        "CREATE CONSTRAINT type_name IF NOT EXISTS "
        "FOR (t:ClauseType) REQUIRE t.name IS UNIQUE",
    ]
    with driver.session() as session:
        for constraint in constraints:
            session.run(constraint)


driver = get_driver()
create_constraints(driver)
## end::code_neo4j_constraints[]

# This function parses the SLA markdown file into Clause objects.
# It treats each '##' heading as a clause title and the following lines as the clause text.


# tag::code_sla_chunking[]
@dataclass
class Clause:
    id: str
    title: str
    text: str
    order: int
    clause_type: str = "Other"


def parse_sla_file(path: str, sla_id: str) -> List[Clause]:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    sections = re.split(r"^##\s+", content, flags=re.MULTILINE)[1:]
    clauses = []

    for idx, section in enumerate(sections, start=1):
        lines = section.strip().splitlines()
        if not lines:
            continue
        title = lines[0].strip()
        text = "\n".join(lines[1:]).strip()

        clauses.append(Clause(id=f"{sla_id}_C{idx}", title=title, text=text, order=idx))

    return clauses


sla_id = "SLA1"
sla_title = "Cloud Compute Service Level Agreement (SLA)"
sla_file_path = "./sample_data/SLA1_SUP1.md"

clauses = parse_sla_file(path=sla_file_path, sla_id=sla_id)
# end::code_sla_chunking[]


# Finally, this function writes the SLA and all Clause nodes to Neo4j and wires them up:
# - it creates the SLA node
# - it creates Clause nodes and HAS_CLAUSE relationships from the SLA
# - it links clauses in order using NEXT
# - it calls add_clause_types to attach semantic ClauseType nodes.
## tag::write_to_neo4j[]
def write_sla_and_clauses(
    driver, sla_id: str, sla_title: str, clauses: List[Clause]
) -> None:
    with driver.session() as session:
        # SLA node
        session.run(
            """
            MERGE (s:SLA {id: $id})
            SET s.title = $title
            """,
            id=sla_id,
            title=sla_title,
        )

        # Clause nodes + HAS_CLAUSE
        for c in clauses:
            session.run(
                """
                MERGE (cl:Clause {id: $id})
                SET cl.title = $title,
                    cl.text = $text,
                    cl.order = $order
                """,
                id=c.id,
                title=c.title,
                text=c.text,
                order=c.order,
                ctype=c.clause_type,
            )
            session.run(
                """
                MATCH (s:SLA {id: $sla_id})
                MATCH (cl:Clause {id: $cid})
                MERGE (s)-[:HAS_CLAUSE]->(cl)
                """,
                sla_id=sla_id,
                cid=c.id,
            )

        # NEXT relationships to preserve order
        for prev, nxt in zip(clauses, clauses[1:]):
            session.run(
                """
                MATCH (a:Clause {id: $p})
                MATCH (b:Clause {id: $n})
                MERGE (a)-[:NEXT]->(b)
                """,
                p=prev.id,
                n=nxt.id,
            )


write_sla_and_clauses(driver, sla_id, sla_title, clauses)
## end::write_to_neo4j[]


"""
Jetzt möchte ich den Klauseltypen (ClauseType) hinzufügen, um die Klauseln semantisch zu kategorisieren.
Dazu werde ich eine einfache Heuristik verwenden, um den Typ basierend auf dem Titel der Klausel zuzuordnen.
It maps titles like "Availability" or "Support" to semantic types such as Availability or Support.
"""


## tag::find_clause_type[]
def infer_clause_type(title: str) -> str:
    """Infer ClauseType based on keywords in the title."""
    title_lower = title.lower()
    keywords = {
        "Availability": ["availability", "uptime"],
        "Support": ["support", "response time", "incident"],
        "Maintenance": ["maintenance"],
        "DataProtection": ["data protection", "gdpr", "privacy"],
        "Liability": ["liability"],
        "Termination": ["termination"],
    }

    for clause_type, words in keywords.items():
        if any(word in title_lower for word in words):
            return clause_type
    return "Other"


for c in clauses:
    c.clause_type = infer_clause_type(c.title)
## end::find_clause_type[]

"""
Jetzt wo ich den Klauseltypen (ClauseType) zugewiesen habe, werde ich ClauseType-Knoten erstellen und
jede Klausel mit ihrem Typ verbinden.
Dies ermöglicht es mir, später Klauseln nach ihrer semantischen Kategorie abzufragen.
Am ende hab ich einen OF_TYPE Beziehung zwischen Clause und ClauseType.
"""


## tag::add_clause_types[]
def add_clause_types(session, clauses: List[Clause]):
    # Create ClauseType nodes
    types = [{"clause_type": c.clause_type} for c in clauses]
    session.run(
        """
        UNWIND $rows AS row
        MERGE (t:ClauseType {name: row.clause_type})
    """,
        rows=types,
    )

    # Link clauses to their types
    links = [{"id": c.id, "type": c.clause_type} for c in clauses]
    session.run(
        """
        UNWIND $rows AS row
        MATCH (cl:Clause {id: row.id})
        MATCH (t:ClauseType {name: row.type})
        MERGE (cl)-[:OF_TYPE]->(t)
    """,
        rows=links,
    )


add_clause_types(driver.session(), clauses)
## end::add_clause_types[]

"""
Jetzt schauen wir mal ob alles geklappt hat. 
Ich werde einige Cypher-Abfragen ausführen, um die Knoten und Beziehungen zu überprüfen.
"""
with driver.session() as session:
    sla_result = session.run("MATCH (s:SLA) RETURN s.id AS id, s.title AS title")
    print("SLAs in the graph:")
    for record in sla_result:
        print(f"- {record['id']}: {record['title']}")

    clause_result = session.run(
        """
        MATCH (s:SLA)-[:HAS_CLAUSE]->(c:Clause)
        RETURN c.id AS id, c.title AS title, c.clause_type AS type
        ORDER BY c.order
        """
    )
    print("\nClauses in the graph:")
    for record in clause_result:
        print(f"- {record['id']}: {record['title']} (Type: {record['type']})")

driver.close()
