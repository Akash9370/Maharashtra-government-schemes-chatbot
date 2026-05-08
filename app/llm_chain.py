import os
from dotenv import load_dotenv
import google.generativeai as genai
#from langchain_google_genai import ChatGoogleGenerativeAI
from retriever import get_retriever
from app.crud import get_all_schemes

def detect_query_category(query):
    q = query.lower()

    if any(w in q for w in ["farmer", "farmers", "agriculture", "krishi", "kisan", "shetkari"]):
        return "farmer"

    if any(w in q for w in ["student", "students", "scholarship", "education", "college", "school"]):
        return "student"

    if any(w in q for w in ["health", "hospital", "medical", "arogya", "davakhana"]):
        return "health"

    if any(w in q for w in ["pension", "old age", "senior citizen", "widow", "niradhar", "disability", "divyang"]):
        return "welfare"

    if any(w in q for w in ["women", "woman", "girl", "mahila", "kanya", "ladki"]):
        return "women"

    if any(w in q for w in ["house", "housing", "home", "awas", "gharkul"]):
        return "housing"

    if any(w in q for w in ["employment", "job", "skill", "rojgar", "livelihood"]):
        return "employment"

    # Keep loan LAST so pension/welfare/other support schemes don't get misclassified
    if any(w in q for w in ["loan", "karj", "bank", "credit"]):
        return "loan"

    return None


load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("models/gemini-flash-latest")


PROMPT_TEMPLATE = """
You are a helpful assistant specializing in Maharashtra government schemes.

STRICT INSTRUCTIONS:
- Answer ONLY using the provided context.
- Do NOT add schemes that are not in the context.
- If no relevant scheme is found, say so politely.
- If the user asks a follow-up like "more", "only 2?", "second scheme", or "what about other?", use the conversation history to understand the previous topic.

LANGUAGE RULE:
- If user asks in Hindi → answer ONLY in Hindi
- If user asks in Marathi → answer ONLY in Marathi
- Otherwise → answer in English
- Do NOT mix languages

FORMAT RULE (VERY IMPORTANT):
- Each scheme must be clearly separated
- Use numbering (1, 2, 3...)
- Use this exact structure:

1. Scheme Name:
   - Eligibility:
   - Benefits:

2. Scheme Name:
   - Eligibility:
   - Benefits:

- Keep spacing clean for readability
- Do NOT write long paragraphs
- Keep answers concise but informative

Conversation History:
{chat_history}

Relevant Schemes:
{context}

User Question:
{question}

Answer:
"""

CATEGORY_KEYWORDS = {
    "farmer": ["farmer", "agriculture", "krishi", "kisan", "shetkari", "crop", "irrigation", "dairy", "livestock", "fisheries"],
    "student": ["student", "scholarship", "school", "college", "education", "hostel", "exam", "eklavy", "vidya", "shishya"],
    "health": ["health", "hospital", "medical", "treatment", "insurance", "arogya", "davakhana", "ayushman"],
    "welfare": ["pension", "old age", "senior citizen", "niradhar", "disability", "divyang", "widow", "destitute", "nivrutti"],
    "housing": ["housing", "house", "awas", "gharkul", "property"],
    "women": ["women", "girl", "mahila", "kanya", "ladki"],
    "employment": ["job", "employment", "skill", "rojgar", "livelihood"],
    "loan": ["loan", "karj", "bank", "credit", "finance", "interest"],
}


def scheme_matches_category(s, category):
    db_category = (s.category or "").lower().strip()

    text = f"""
    {s.name}
    {s.category}
    {s.eligibility}
    {s.benefits}
    {s.description}
    """.lower()

    # Trust correct DB category if present
    if db_category == category:
        return True

    # Fallback to keyword matching for old General/empty categories
    return any(w in text for w in CATEGORY_KEYWORDS.get(category, []))
def ask_question(question: str, chat_history: str = "") -> dict:
    combined_query = f"{chat_history} {question}"
    category = detect_query_category(combined_query)

    # CATEGORY ROUTE: for queries like farmer schemes, pension schemes, student schemes
    if category:
        all_schemes = get_all_schemes()

        matched_docs = []

        for s in all_schemes:
            if scheme_matches_category(s, category):
                matched_docs.append(f"""
        Scheme Name: {s.name}
        Eligibility: {s.eligibility}
        Benefits: {s.benefits}
        """)

        matched_docs = matched_docs[:15]

        if not matched_docs:
            return {
                "answer": f"No {category} schemes found in the knowledge base.",
                "sources": []
            }

        context = "\n\n".join(matched_docs)

    # SEMANTIC ROUTE: for natural queries like "I need hostel help for college"
    else:
        retriever = get_retriever(k=10)
        query = question + " Maharashtra government scheme"
        docs = retriever.invoke(query)

        docs = docs[:15]

        if not docs:
            return {
                "answer": "No relevant schemes found. Please try rephrasing your query.",
                "sources": []
            }

        context = "\n\n".join([doc.page_content for doc in docs])

    prompt = PROMPT_TEMPLATE.format(
        context=context,
        question=question,
        chat_history=chat_history
    )

    response = model.generate_content(prompt)

    return {
        "answer": response.text,
        "sources": []
    }