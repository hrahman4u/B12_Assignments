import logging

# Hide the harmless Neo4j "deprecated" warning
logging.getLogger("neo4j.notifications").setLevel(logging.ERROR)

import streamlit as st

from kg_rag import ask  # the brain we built in Step 8

# --- 1. CHANGE HEADER & TAB ICONS HERE ---
st.set_page_config(page_title="Tamil Nadu Schemes Chatbot", page_icon="🌾")
st.title("🌾 Tamil Nadu Schemes Chatbot")
st.caption("Knowledge Graph RAG by Habib Rahman using Neo4j + LangChain + OpenAI")

# --- 2. SET CUSTOM CHAT AVATARS HERE ---
# You can use emojis, local image paths (e.g., "user.png"), or image URLs
AVATARS = {
    "user": "🧑‍🌾",
    "assistant": "🤖"
}

# ---------- Sidebar ----------
with st.sidebar:
    st.header("About")
    st.write(
        "Ask about Tamil Nadu Government Schemes. "
        "Answers are sourced from a Neo4j knowledge graph built from the TN.GOV.IN scheme list."
    )
    st.subheader("What would you like to know?")
    examples = [
        "Which schemes are for farmers?",
        "How do I apply for Training to Farmers?",
        "Is there any subsidy for stamp duty?",
        "Which schemes give grants?",
        "Which schemes support women?",
        "What schemes are available for students?",
        "Which schemes help small businesses?",
        "How can I apply for a government subsidy?",
    ]
    for example in examples:
        if st.button(example, use_container_width=True):
            st.session_state["pending"] = example
    if st.button("Clear chat", use_container_width=True):
        st.session_state["messages"] = []
        st.rerun()

# ---------- Chat history (kept between reruns) ----------
if "messages" not in st.session_state:
    st.session_state["messages"] = []


def show_sources(sources):
    if sources:
        with st.expander("Sources"):
            for s in sources:
                st.markdown(f"- [{' '.join(s['name'].split())}]({s['url']})")


for message in st.session_state["messages"]:
    # Pass the custom avatar based on the message role
    with st.chat_message(message["role"], avatar=AVATARS.get(message["role"])):
        st.markdown(message["content"])
        show_sources(message.get("sources"))

# ---------- New question ----------
pending = st.session_state.pop("pending", None)
question = st.chat_input("Ask about Tamil Nadu Government Schemes...") or pending

if question:
    st.session_state["messages"].append({"role": "user", "content": question})
    
    # Use custom user avatar
    with st.chat_message("user", avatar=AVATARS["user"]):
        st.markdown(question)

    # Use custom assistant avatar
    with st.chat_message("assistant", avatar=AVATARS["assistant"]):
        with st.spinner("Searching the knowledge graph..."):
            answer, sources = ask(question)
        st.markdown(answer)

        # Show only the sources the answer actually mentions
        answer_text = " ".join(answer.split()).lower()
        used = [s for s in sources if " ".join(s["name"].split()).lower() in answer_text]
        if not used and "do not have" not in answer_text:
            used = sources
        show_sources(used)

    st.session_state["messages"].append(
        {"role": "assistant", "content": answer, "sources": used}
    )