
import os
import tempfile

import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.messages import SystemMessage, HumanMessage


st.set_page_config(page_title="Multi-PDF RAG", page_icon="📚")
st.title("📚 Multi-PDF RAG Assistant")
st.write("Upload multiple PDFs and ask questions across your documents.")

# 1. Check the API key
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("OPENAI_API_KEY is missing. Set it in your terminal.")
    st.stop()

# 2. Upload multiple PDFs
files = st.file_uploader(
    "Upload your PDF files",
    type=["pdf"],
    accept_multiple_files=True,
)

# 3. Index every PDF into one FAISS store
if st.button("Build / Rebuild Index", disabled=not files):
    all_chunks = []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
    )

    with st.spinner("Reading and indexing PDFs..."):
        for uploaded_file in files:
            temp_path = None

            try:
                # Save the uploaded PDF temporarily
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".pdf"
                ) as temp_file:
                    temp_file.write(uploaded_file.getvalue())
                    temp_path = temp_file.name

                # Extract pages and preserve metadata
                pages = PyPDFLoader(temp_path).load()

                for page in pages:
                    page.metadata["source"] = uploaded_file.name

                # Split this PDF into chunks
                chunks = splitter.split_documents(pages)
                all_chunks.extend(chunks)

            except Exception as e:
                st.error(f"Could not read {uploaded_file.name}: {e}")

            finally:
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)

        if all_chunks:
            try:
                embeddings = OpenAIEmbeddings(
                    model="text-embedding-3-small",
                    api_key=api_key,
                )

                store = FAISS.from_documents(
                    all_chunks, embeddings
                )

                st.session_state.store = store
                st.session_state.indexed_files = [
                    f.name for f in files
                ]
                st.session_state.chunk_count = len(all_chunks)

                st.success(
                    f"Indexed {len(all_chunks)} chunks successfully!"
                )
            except Exception as e:
                st.error(f"Indexing failed: {e}")
        else:
            st.warning("No readable PDF chunks were found.")

# 4. Display index information
if "store" in st.session_state:
    st.info(
        f"Indexed {st.session_state.chunk_count} chunks from: "
        + ", ".join(st.session_state.indexed_files)
    )

    # 5. Ask a question
    question = st.text_input(
        "Ask a question about your PDFs"
    )

    if st.button("Get Answer", disabled=not question.strip()):
        with st.spinner("Searching documents and preparing answer..."):
            try:
                retriever = st.session_state.store.as_retriever(
                    search_kwargs={"k": 5}
                )
                docs = retriever.invoke(question)

                if not docs:
                    st.warning("No relevant document chunks found.")
                else:
                    context = "\n\n".join(
                        f"Source: {d.metadata.get('source', 'Unknown')}, "
                        f"page {d.metadata.get('page', 0) + 1}\n"
                        f"{d.page_content}"
                        for d in docs
                    )

                    llm = ChatOpenAI(
                        model="gpt-4o-mini",
                        temperature=0,
                        api_key=api_key,
                    )

                    response = llm.invoke([
                        SystemMessage(
                            content=(
                                "Answer using only the supplied document "
                                "context. If the context does not answer "
                                "the question, say so. If documents "
                                "disagree, explain the disagreement."
                            )
                        ),
                        HumanMessage(
                            content=(
                                f"Question: {question}\n\n"
                                f"Document context:\n{context}"
                            )
                        ),
                    ])

                    st.subheader("Answer")
                    st.write(response.content)

                    st.subheader("Sources")
                    seen = set()

                    for doc in docs:
                        filename = doc.metadata.get(
                            "source", "Unknown"
                        )
                        page = doc.metadata.get("page", 0) + 1
                        source = (filename, page)

                        if source not in seen:
                            st.caption(
                                f"{filename} — page {page}"
                            )
                            seen.add(source)

            except Exception as e:
                st.error(f"Could not answer the question: {e}")
