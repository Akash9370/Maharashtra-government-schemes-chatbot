from dotenv import load_dotenv
import os
import pandas as pd
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

load_dotenv()


def load_schemes_to_vectorstore(csv_path: str = None, persist_dir: str = "info/chroma_db"):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



    df = pd.read_csv(csv_path)

    documents = []
    for _, row in df.iterrows():
        content = f"""
        This is a government scheme in Maharashtra.

        Scheme Name: {row['Scheme Name']}

        This scheme is for:
        {row['Eligibility Criteria']}

        Benefits:
        {row['Scheme Benefits']}

        Relevant keywords: Scheduled Caste SC, OBC, student, education, scholarship, 10th pass, 12th pass, college, financial assistance
        """
        documents.append(Document(page_content=content, metadata={"scheme_name": row['Scheme Name']}))
    hf_token = os.getenv("HF_TOKEN")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",

    )
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_dir
    )

    print(f"✅ Indexed {len(documents)} schemes into ChromaDB")
    return vectorstore


if __name__ == "__main__":
    load_schemes_to_vectorstore()
