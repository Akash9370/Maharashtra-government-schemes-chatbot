import streamlit as st

@st.cache_resource(show_spinner=False)
def get_retriever(persist_dir="info/chroma_db", k=6):
    from langchain_community.vectorstores import Chroma
    from langchain_huggingface import HuggingFaceEmbeddings

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    vectorstore = Chroma(
        persist_directory=persist_dir
    )

    return vectorstore.as_retriever(search_kwargs={"k": k})