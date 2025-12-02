"""Recipe 02: Extending the SLA knowledge graph with
structured company data.

Imports CSV master data and links to existing SLA / Clause
structure.
Expected CSV files (pass --data-dir):
- companies.csv (supplier_id,name,country,address_id,industry)
- addresses.csv (address_id,street,city,postal_code,country)
- spend_2024.csv (supplier_id,spend_eur,spend_category)
- slas.csv (sla_id,supplier_id,title,service_name,
            effective_date,governing_law)

Run:
python recipe02_enrich_company_data.py --data-dir data

pip install pandas neo4j python-dotenv
"""

from __future__ import annotations
import argparse
import os
from typing import Any, Dict, Optional
import pandas as pd
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()


def get_driver():
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USERNAME")
    pwd = os.getenv("NEO4J_PASSWORD")
    return GraphDatabase.driver(uri, auth=(user, pwd))


## tag::load_companies[]
def load_companies(driver, companies_csv_path: str) -> None:
    df = pd.read_csv(companies_csv_path)

    with driver.session() as session:
        session.run(
            """
            UNWIND $rows AS row
            MERGE (c:Company {supplier_id: row.supplier_id})
            ON CREATE SET c.name=row.name, 
                          c.country=row.country, 
                          c.industry=row.industry
            SET c.industry = row.industry
            """,
            {"rows": df.to_dict(orient="records")},
        )


driver = get_driver()
companies_csv_path = "sample_data/companies.csv"
load_companies(driver, companies_csv_path)
## end::load_companies[]


## tag::load_addresses[]
def load_addresses(driver, addresses_csv_path: str) -> None:
    df = pd.read_csv(addresses_csv_path)
    with driver.session() as session:
        session.run(
            """
            UNWIND $rows AS row
            MERGE (a:Address {id: row.address_id})
            ON CREATE SET a.street = row.street, 
                          a.city = row.city, 
                          a.postal_code = row.postal_code, 
                          a.country = row.country
            """,
            {"rows": df.to_dict(orient="records")},
        )


addresses_csv_path = "sample_data/addresses.csv"
load_addresses(driver, addresses_csv_path)

## end::load_addresses[]


## tag::connect_company_addresses[]
def connect_company_addresses(driver, companies_csv_path: str) -> None:
    df = pd.read_csv(companies_csv_path)[["supplier_id", "address_id"]]
    with driver.session() as session:
        session.run(
            """
            UNWIND $rows AS row
            MATCH (c:Company {supplier_id: row.supplier_id})
            MATCH (a:Address {id: row.address_id})
            MERGE (c)-[:LOCATED_AT]->(a)
            """,
            {"rows": df.to_dict(orient="records")},
        )


companies_csv_path = "sample_data/companies.csv"
connect_company_addresses(driver, companies_csv_path)
## end::connect_company_addresses[]


## tag::load_spend[]
def load_spend(driver, spend_csv_path: str) -> None:
    df = pd.read_csv(spend_csv_path)
    with driver.session() as session:
        session.run(
            """
            UNWIND $rows AS row
            MATCH (c:Company {supplier_id: row.supplier_id})
            SET c.spend_2024 = toFloat(row.spend_eur), 
                c.spend_category = row.spend_category
            """,
            {"rows": df.to_dict(orient="records")},
        )


spend_csv_path = "sample_data/spend_2024.csv"
load_spend(driver, spend_csv_path)
## end::load_spend[]


## tag::load_slas[]
def load_slas(driver, sla_csv_path: str) -> None:
    df = pd.read_csv(sla_csv_path)
    df["effective_date"] = df["effective_date"].replace({"N/A": None})
    df["effective_date"] = df["effective_date"].where(
        df["effective_date"].notna(), None
    )
    with driver.session() as session:
        session.run(
            """
            UNWIND $rows AS row
            MATCH (c:Company {supplier_id: row.supplier_id})
            MERGE (s:SLA {id: row.sla_id})
            ON CREATE SET s.title = row.title, 
                          s.service_name = row.service_name,
                          s.governing_law = row.governing_law,
                          s.effective_date = CASE 
                            WHEN row.effective_date IS NOT NULL 
                            THEN date(row.effective_date) 
                            ELSE NULL END
            MERGE (c)-[:HAS_SLA]->(s)
            """,
            {"rows": df.to_dict(orient="records")},
        )


sla_csv_path = "sample_data/slas.csv"
load_slas(driver, sla_csv_path)
## end::load_slas[]
