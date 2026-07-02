import streamlit as st

@st.cache_resource(show_spinner=False)
def get_vectorstore(persist_dir="info/chroma_db"):
    from langchain_community.vectorstores import Chroma
    from langchain_huggingface import HuggingFaceEmbeddings

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    return Chroma(
        persist_directory=persist_dir,
        embedding_function=embeddings
    )

def get_retriever(persist_dir="info/chroma_db", k=10):
    vectorstore = get_vectorstore(persist_dir)
    return vectorstore.as_retriever(search_kwargs={"k": k})