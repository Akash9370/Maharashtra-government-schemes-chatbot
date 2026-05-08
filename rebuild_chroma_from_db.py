from app.crud import get_all_schemes
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import os

def rebuild():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",

    )

    schemes = get_all_schemes()

    docs = [
        f"""
Scheme Name: {s.name}
Description: {s.description}
Eligibility: {s.eligibility}
Benefits: {s.benefits}
State: {s.state}
Category: {s.category}
"""
        for s in schemes
    ]

    vectorstore = Chroma.from_texts(
        texts=docs,
        embedding=embeddings,
        persist_directory="info/chroma_db"
    )

    print("Chroma rebuilt successfully")

if __name__ == "__main__":
    rebuild()