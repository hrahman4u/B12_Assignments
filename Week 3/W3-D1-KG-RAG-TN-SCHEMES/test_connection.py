import os
import sys
import certifi
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Fix secure-connection problems on Windows
if sys.platform == "win32":
    os.environ.setdefault("SSL_CERT_FILE", certifi.where())

load_dotenv()

uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(uri, auth=(user, password))
driver.verify_connectivity()
print("Connected to Neo4j successfully!")
driver.close()