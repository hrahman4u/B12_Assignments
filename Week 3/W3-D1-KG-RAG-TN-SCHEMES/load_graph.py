import json
import os
import sys

import certifi
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Fix secure-connection problems on Windows
if sys.platform == "win32":
    os.environ.setdefault("SSL_CERT_FILE", certifi.where())

load_dotenv()
driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD")),
)


def split_values(text):
    """'Farmers, Women' -> ['Farmers', 'Women']"""
    return [part.strip() for part in text.split(",") if part.strip()]


with open("schemes_data.json", "r", encoding="utf-8") as f:
    schemes = json.load(f)

with driver.session() as session:
    # Clean start: delete only the nodes this project creates
    session.run(
        "MATCH (n) WHERE n:Scheme OR n:Sponsor OR n:Beneficiary OR n:BenefitType "
        "DETACH DELETE n"
    )

    for scheme in schemes:
        url = scheme["url"]

        # 1. The Scheme node itself
        session.run(
            """
            MERGE (s:Scheme {url: $url})
            SET s.name = $name,
                s.funding_pattern = $funding,
                s.description = $description,
                s.submit_to = $submit_to
            """,
            url=url,
            name=scheme["name"],
            funding=scheme.get("funding_pattern", ""),
            description=scheme.get("description", ""),
            submit_to=scheme.get("submit_to", ""),
        )

        # 2. Sponsor nodes + relationship
        for sponsor in split_values(scheme.get("sponsored_by", "")):
            session.run(
                """
                MATCH (s:Scheme {url: $url})
                MERGE (p:Sponsor {name: $value})
                MERGE (s)-[:SPONSORED_BY]->(p)
                """,
                url=url, value=sponsor,
            )

        # 3. Beneficiary nodes + relationship
        for person in split_values(scheme.get("beneficiaries", "")):
            session.run(
                """
                MATCH (s:Scheme {url: $url})
                MERGE (b:Beneficiary {name: $value})
                MERGE (s)-[:FOR_BENEFICIARY]->(b)
                """,
                url=url, value=person,
            )

        # 4. BenefitType nodes + relationship
        for benefit in split_values(scheme.get("benefit_type", "")):
            session.run(
                """
                MATCH (s:Scheme {url: $url})
                MERGE (t:BenefitType {name: $value})
                MERGE (s)-[:OFFERS]->(t)
                """,
                url=url, value=benefit,
            )

    # A search index so the chatbot can find schemes by words (used in Step 8)
    session.run(
        "CREATE FULLTEXT INDEX scheme_text IF NOT EXISTS "
        "FOR (s:Scheme) ON EACH [s.name, s.description, s.funding_pattern, s.submit_to]"
    )

    # ---------- Report ----------
    print("Loaded into Neo4j!\n")
    for label in ["Scheme", "Sponsor", "Beneficiary", "BenefitType"]:
        count = session.run(f"MATCH (n:{label}) RETURN count(n) AS c").single()["c"]
        print(f"{label} nodes: {count}")
    rels = session.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]
    print("Relationships:", rels)

    for label in ["Sponsor", "Beneficiary", "BenefitType"]:
        names = session.run(f"MATCH (n:{label}) RETURN n.name AS n ORDER BY n").values()
        print(f"\n{label} values:", [row[0] for row in names])

driver.close()