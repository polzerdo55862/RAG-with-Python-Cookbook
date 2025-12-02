"""Recipe 03: Cypher query examples wrapped as executable Python functions.

Each function demonstrates a common SLA knowledge graph query and returns
structured results instead of printing raw Cypher. The original chapter
showed plain Cypher blocks; here they are wrapped so they can be imported
or executed directly. Environment variables (NEO4J_URI, NEO4J_USERNAME,
NEO4J_PASSWORD) must be set, e.g. via a .env file.
"""

from __future__ import annotations
import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()


def get_driver():
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USERNAME")
    pwd = os.getenv("NEO4J_PASSWORD")
    if not uri or not user or not pwd:
        raise RuntimeError("Missing Neo4j env vars")
    return GraphDatabase.driver(uri, auth=(user, pwd))


# tag::code_list_clauses_for_sla[]
def list_clauses_for_sla(sla_id: str) -> List[Dict[str, Any]]:
    """Return all clauses for one SLA ordered by their original position."""
    cypher = """
    MATCH (s:SLA {id: $sla_id})-[:HAS_CLAUSE]->(cl:Clause)
    RETURN cl.order AS order,
           cl.title AS title,
           cl.text AS text
    ORDER BY order
    """
    driver = get_driver()
    with driver.session() as session:
        response = session.run(cypher, sla_id=sla_id)
        records = [r.data() for r in response]
        return records


records_clauses = list_clauses_for_sla(sla_id="SLA1")
# end::code_list_clauses_for_sla[]


# tag::code_clauses_of_type[]
def clauses_of_type(clause_type: str) -> List[Dict[str, Any]]:
    """List all clauses of a specific ClauseType across suppliers."""
    cypher = """
    MATCH (c:Company)-[:HAS_SLA]->(s:SLA)-[:HAS_CLAUSE]->(cl:Clause)
    MATCH (cl)-[:OF_TYPE]->(t:ClauseType {name: $clause_type})
    RETURN c.name AS company,
           s.id AS sla_id,
           cl.order AS clause_order,
           cl.title AS clause_title,
           cl.text AS clause_text
    ORDER BY company, sla_id, clause_order
    """
    driver = get_driver()
    with driver.session() as session:
        return [r.data() for r in session.run(cypher, clause_type=clause_type)]


records_clause_types = clauses_of_type(clause_type="Termination")

# end::code_clauses_of_type[]


# tag::code_high_spend_missing_termination[]
def high_spend_missing_termination(min_spend: float) -> List[Dict[str, Any]]:
    """Return companies above min_spend whose SLAs lack a termination clause."""
    cypher = """
    MATCH (c:Company)-[:HAS_SLA]->(s:SLA)
    WHERE c.spend_2024 > $min_spend
    OPTIONAL MATCH (s)-[:HAS_CLAUSE]->(cl:Clause)-[:OF_TYPE]->(t:ClauseType {name: "Termination"})
    WITH c, s, count(cl) AS num_termination
    WHERE num_termination = 0
    RETURN c.name AS company,
           c.spend_2024 AS spend_2024,
           s.id AS sla_id
    ORDER BY spend_2024 DESC
    """
    driver = get_driver()

    with driver.session() as session:
        return [r.data() for r in session.run(cypher, min_spend=min_spend)]


records_min_spend = high_spend_missing_termination(min_spend=500000)
# end::code_high_spend_missing_termination[]


# tag::code_availability_clauses[]
def availability_clauses(search_phrase: str) -> List[Dict[str, Any]]:
    """Inspect availability clauses per supplier."""
    cypher = """
    MATCH (c:Company)-[:HAS_SLA]->(s:SLA)-[:HAS_CLAUSE]->(cl:Clause)
    MATCH (cl)-[:OF_TYPE]->(t:ClauseType {name: "Availability"})
    WHERE toLower(cl.text) CONTAINS toLower($phrase)
    RETURN c.name AS company,
           s.id AS sla_id,
           cl.order AS clause_order,
           cl.text AS availability_text
    ORDER BY company, sla_id, clause_order
    """
    driver = get_driver()
    with driver.session() as session:
        return [r.data() for r in session.run(cypher, phrase=search_phrase)]


availability_clauses_records = availability_clauses(search_phrase="99.9")
# end::code_availability_clauses[]


# tag::code_eu_data_protection_clauses[]
def eu_data_protection_clauses(countries: list[str]):
    """Retrieve data protection clauses for suppliers in given EU countries."""
    cypher = """
    MATCH (c:Company)-[:LOCATED_AT]->(a:Address)
    WHERE a.country IN $countries
    MATCH (c)-[:HAS_SLA]->(s:SLA)-[:HAS_CLAUSE]->(cl:Clause)
    MATCH (cl)-[:OF_TYPE]->(t:ClauseType {name: "DataProtection"})
    RETURN c.name AS company,
           a.country AS country,
           s.id AS sla_id,
           cl.order AS clause_order,
           cl.text AS data_protection_clause
    ORDER BY country, company, sla_id, clause_order
    """
    driver = get_driver()

    with driver.session() as session:
        return [r.data() for r in session.run(cypher, countries=countries)]


countries = ["Germany", "France", "Netherlands"]
eu_data_protection_clauses_records = eu_data_protection_clauses(countries=countries)
# end::code_eu_data_protection_clauses[]
