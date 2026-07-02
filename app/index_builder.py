from app.crud import get_all_schemes
import os
from dotenv import load_dotenv
import shutil
from app.categories import detect_category as guess_category

load_dotenv()

PERSIST_DIR = "info/chroma_db"

CATEGORY_MAP = {
    "farmer": "farmer agriculture crop land rural irrigation subsidy",
    "student": "student education scholarship school college hostel",
    "health": "health hospital insurance medical treatment healthcare",
    "welfare": "pension old age senior citizen disability niradhar widow financial assistance support",
    "housing": "housing home loan property subsidy housing scheme",
    "women": "women empowerment girl child maternity support",
    "employment": "jobs employment skill training livelihood",
    "rural": "rural development village livelihood support",
    "loan": "loan subsidy finance credit bank interest scheme",
}



def detect_category(s):
    if s.category and s.category.strip().lower() != "general":
        return s.category.strip().lower()          # trust the DB if it's set
    text = " ".join([s.name or "", s.eligibility or "", s.benefits or "", s.description or ""])
    return guess_category(text)

import gc
import time

def safe_rmtree(path, retries=10, delay=1.0):
    for attempt in range(retries):
        try:
            if os.path.exists(path):
                shutil.rmtree(path)
            return
        except PermissionError:
            gc.collect()
            if attempt == retries - 1:
                raise
            time.sleep(delay)

def _scheme_to_text(s):
    category = detect_category(s)
    extra_keywords = CATEGORY_MAP.get(category, "")
    text = f"""Government Scheme in {s.state or 'Maharashtra'}.

Scheme Name: {s.name}
Category: {category}

Eligibility:
{s.eligibility}

Description:
{s.description}

Benefits:
{s.benefits}

Search Tags: {category}, {extra_keywords}, government scheme Maharashtra"""
    return text, category


def add_scheme_to_index(scheme):
    from app.retriever import get_vectorstore
    vectorstore = get_vectorstore()

    text, category = _scheme_to_text(scheme)
    vectorstore.add_texts(
        texts=[text],
        metadatas=[{"name": scheme.name, "category": category}]
    )


def delete_scheme_from_index(name):
    from app.retriever import get_vectorstore
    vectorstore = get_vectorstore()
    vectorstore._collection.delete(where={"name": name})


def build_index():
    from langchain_community.vectorstores import Chroma
    from langchain_huggingface import HuggingFaceEmbeddings

    schemes = get_all_schemes()

    if not schemes:
        print("No schemes found in the database — skipping index build.")
        return None

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    docs = []
    metadatas = []

    for s in schemes:
        state = s.state or "Maharashtra"
        category = detect_category(s)
        extra_keywords = CATEGORY_MAP.get(category, "")

        text = f"""Government Scheme in {state}.

Scheme Name: {s.name}
Category: {category}

Eligibility:
{s.eligibility}

Description:
{s.description}

Benefits:
{s.benefits}

Search Tags: {category}, {extra_keywords}, government scheme Maharashtra"""

        docs.append(text)
        metadatas.append({
            "name": s.name,
            "category": category,
        })

    try:
        safe_rmtree(PERSIST_DIR)

        vectorstore = Chroma.from_texts(
            texts=docs,
            embedding=embeddings,
            metadatas=metadatas,          # <-- this is the fix that makes `sources` work
            persist_directory=PERSIST_DIR
        )
        vectorstore.persist()

        print(f"Index built successfully with {len(docs)} schemes")
        return vectorstore

    except Exception as e:
        print(f"Failed to build index: {e}")
        raise  # re-raise so the caller (Streamlit) can catch and show a message


if __name__ == "__main__":
    build_index()