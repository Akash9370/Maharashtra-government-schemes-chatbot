from app.crud import get_all_schemes
import os
from dotenv import load_dotenv
import shutil

load_dotenv()
print("HF_TOKEN loaded:", bool(os.getenv("HF_TOKEN")))

PERSIST_DIR = "info/chroma_db"

def build_index():
    from langchain_community.vectorstores import Chroma
    from langchain_huggingface import HuggingFaceEmbeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    schemes = get_all_schemes()

    docs = []

    category_map = {
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
        name = (s.name or "").lower()
        eligibility = (s.eligibility or "").lower()
        benefits = (s.benefits or "").lower()
        description = (s.description or "").lower()

        text = f"{name} {eligibility} {benefits} {description}"

        # 🌾 FARMER
        if any(w in text for w in [
            "farmer", "agriculture", "krishi", "kisan", "shetkari",
            "crop", "irrigation", "dairy", "livestock", "fisheries"
        ]):
            return "farmer"

        # 🎓 STUDENT
        if any(w in text for w in [
            "student", "scholarship", "school", "college",
            "education", "hostel", "exam", "eklavy", "vidya", "shishya"
        ]):
            return "student"

        # 🏥 HEALTH
        if any(w in text for w in [
            "health", "hospital", "medical", "treatment",
            "insurance", "arogya", "davakhana", "ayushman"
        ]):
            return "health"

        if any(w in text for w in [
            "pension", "old age", "senior citizen",
            "niradhar", "disability", "divyang",
            "widow", "destitute", "nivrutti"
        ]):
            return "welfare"

        # 🏠 HOUSING
        if any(w in text for w in [
            "housing", "house", "awas", "gharkul", "property"
        ]):
            return "housing"

        # 👩 WOMEN
        if any(w in text for w in [
            "women", "girl", "mahila", "kanya", "ladki"
        ]):
            return "women"

        # 💼 EMPLOYMENT
        if any(w in text for w in [
            "job", "employment", "skill", "rojgar", "livelihood"
        ]):
            return "employment"

        # 💰 LOAN (LAST)
        if any(w in text for w in [
            "loan", "karj", "bank", "credit", "finance", "interest"
        ]):
            return "loan"

        return "general"
    for s in schemes:
        state = s.state or "Maharashtra"


        category = detect_category(s)

        base_keywords = "government scheme Maharashtra benefits eligibility subsidy support"
        extra_keywords = category_map.get(category, "")

        text = f"""
        Government Scheme in {state}.

        Scheme Name: {s.name}

        IMPORTANT: This is a {category} scheme.
        This scheme is meant for {category} beneficiaries.

        Category: {category}

        Eligibility:
        {s.eligibility}

        Description:
        {s.description}

        Benefits:
        {s.benefits}

        Search Tags:
        {category}, {extra_keywords}, government scheme Maharashtra
        """
        docs.append(text)

        # 🔍 DEBUG
        print(f"EMBEDDING: {s.name} | {category}")

    if os.path.exists(PERSIST_DIR):
        shutil.rmtree(PERSIST_DIR)

    vectorstore = Chroma.from_texts(
        texts=docs,
        embedding=embeddings,
        persist_directory=PERSIST_DIR
    )

    print("Index built successfully")
    return vectorstore

if __name__ == "__main__":
    build_index()