import os
import re
import sys

import certifi
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from neo4j import GraphDatabase

# Fix secure-connection problems on Windows
if sys.platform == "win32":
    os.environ.setdefault("SSL_CERT_FILE", certifi.where())

load_dotenv(override=True)

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD")),
)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

STOP_WORDS = {
    "what", "which", "who", "how", "the", "are", "is", "there", "any", "can",
    "for", "and", "you", "tell", "about", "give", "list", "show", "all", "me",
    "scheme", "schemes", "get", "apply", "does", "do", "with", "from", "this",
    "that", "have", "has", "available", "under", "need", "want", "please",
}


# ---------- Load the names of all Sponsor / Beneficiary / BenefitType nodes ----------
def load_entity_names():
    with driver.session() as session:
        rows = session.run(
            "MATCH (n) WHERE n:Sponsor OR n:Beneficiary OR n:BenefitType "
            "RETURN n.name AS name"
        ).values()
    return [row[0] for row in rows if row[0]]


ENTITY_NAMES = load_entity_names()


# ---------- STEP 1: RETRIEVE ----------
def get_keywords(question):
    words = re.findall(r"[A-Za-z0-9]+", question.lower())
    return [w for w in words if w not in STOP_WORDS and len(w) > 2]


def search_by_text(question, limit=5):
    """Word search over scheme names and descriptions (the full-text index)."""
    keywords = get_keywords(question)
    if not keywords:
        return []
    with driver.session() as session:
        rows = session.run(
            "CALL db.index.fulltext.queryNodes('scheme_text', $q) "
            "YIELD node, score RETURN node.url AS url LIMIT $limit",
            q=" OR ".join(keywords), limit=limit,
        ).values()
    return [row[0] for row in rows]


def search_by_graph(question, limit=8):
    """If the question mentions a node (e.g. 'farmers'), follow its lines to schemes."""
    q = question.lower()
    names = [n for n in ENTITY_NAMES if n.lower().rstrip("s") in q]
    if not names:
        return []
    with driver.session() as session:
        rows = session.run(
            "MATCH (s:Scheme)-[:FOR_BENEFICIARY|OFFERS|SPONSORED_BY]->(n) "
            "WHERE n.name IN $names RETURN DISTINCT s.url AS url LIMIT $limit",
            names=names, limit=limit,
        ).values()
    return [row[0] for row in rows]


def get_scheme_details(urls):
    with driver.session() as session:
        records = session.run(
            """
            MATCH (s:Scheme) WHERE s.url IN $urls
            OPTIONAL MATCH (s)-[:SPONSORED_BY]->(p:Sponsor)
            OPTIONAL MATCH (s)-[:FOR_BENEFICIARY]->(b:Beneficiary)
            OPTIONAL MATCH (s)-[:OFFERS]->(t:BenefitType)
            RETURN s.name AS name, s.url AS url, s.funding_pattern AS funding,
                   s.description AS description, s.submit_to AS submit_to,
                   collect(DISTINCT p.name) AS sponsors,
                   collect(DISTINCT b.name) AS beneficiaries,
                   collect(DISTINCT t.name) AS benefits
            """,
            urls=urls,
        ).data()
    return records


def retrieve(question, max_schemes=6):
    urls = []
    for url in search_by_text(question) + search_by_graph(question):
        if url not in urls:
            urls.append(url)
    return get_scheme_details(urls[:max_schemes])


# ---------- STEP 2: AUGMENT ----------
def build_context(schemes):
    blocks = []
    for s in schemes:
        lines = [f"Scheme: {s['name']}"]
        if s["sponsors"]:
            lines.append(f"Sponsored by: {', '.join(s['sponsors'])}")
        if s["beneficiaries"]:
            lines.append(f"Beneficiaries: {', '.join(s['beneficiaries'])}")
        if s["benefits"]:
            lines.append(f"Type of benefit: {', '.join(s['benefits'])}")
        if s["funding"]:
            lines.append(f"Funding pattern: {s['funding']}")
        if s["submit_to"]:
            lines.append(f"Apply to: {s['submit_to']}")
        if s["description"]:
            lines.append(f"Details: {s['description'][:600]}")
        blocks.append("\n".join(lines))
    return "\n\n---\n\n".join(blocks)


# ---------- STEP 3: GENERATE ----------
prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a helpful assistant for Tamil Nadu government schemes. "
     "Answer ONLY using the context below, which comes from a knowledge graph. "
     "If the answer is not in the context, say you do not have that information. "
     "Mention the scheme names in your answer. "
     "If asked how to apply, include the 'Apply to' information when it is available. "
     "Be clear, friendly and concise."),
    ("human", "Context:\n{context}\n\nQuestion: {question}"),
])
chain = prompt | llm


def ask(question):
    """Returns (answer, list_of_source_schemes)."""
    schemes = retrieve(question)
    if not schemes:
        return "Sorry, I could not find any matching scheme in the knowledge graph.", []
    context = build_context(schemes)
    answer = chain.invoke({"context": context, "question": question}).content
    sources = [{"name": s["name"], "url": s["url"]} for s in schemes]
    return answer, sources


# ---------- Test it in the terminal ----------
if __name__ == "__main__":
    print("Ask about Tamil Nadu schemes (type 'quit' to stop)\n")
    while True:
        question = input("You: ").strip()
        if question.lower() in {"quit", "exit", "q"}:
            break
        if not question:
            continue
        answer, sources = ask(question)
        print("\nBot:", answer)
        if sources:
            print("\nSources:")
            for s in sources:
                print(" -", s["name"])
        print()
    driver.close()