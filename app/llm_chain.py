import os
from dotenv import load_dotenv
from app.crud import get_all_schemes
from app.categories import detect_category, CATEGORY_KEYWORDS  # see note below

load_dotenv()


def detect_query_category(query):
    q = query.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if category == "loan":
            continue  # keep loan last so it doesn't shadow welfare/farmer etc.
        if any(w in q for w in keywords):
            return category
    if any(w in q for w in CATEGORY_KEYWORDS.get("loan", [])):
        return "loan"
    return None


PROMPT_TEMPLATE = """
You are a helpful assistant specializing in Maharashtra government schemes.

STRICT INSTRUCTIONS:
- Answer ONLY using the provided context.
- Do NOT add schemes that are not in the context.
- Do NOT list every scheme from the context.
- Select only schemes directly relevant to the user's exact question.
- Return maximum 5 schemes unless the user asks for more.
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


def scheme_matches_category(s, category):
    db_category = (s.category or "").lower().strip()
    text = " ".join([s.name or "", s.category or "", s.eligibility or "",
                      s.benefits or "", s.description or ""]).lower()

    if db_category == category:
        return True
    return any(w in text for w in CATEGORY_KEYWORDS.get(category, []))


def get_gemini_model():
    import google.generativeai as genai
    api_key = os.getenv("GEMINI_API_KEY")  # <-- fixed to match .env.example
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set. Check your .env file.")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("models/gemini-flash-latest")


def ask_question(question: str, chat_history: str = "") -> dict:
    try:
        combined_query = f"{chat_history} {question}".strip()
        category = detect_query_category(combined_query)

        if category:
            all_schemes = get_all_schemes()
            matched = [s for s in all_schemes if scheme_matches_category(s, category)][:10]

            if not matched:
                return {"answer": f"No {category} schemes found in the knowledge base.", "sources": []}

            context = "\n\n".join(
                f"Scheme Name: {s.name}\nEligibility: {s.eligibility}\nBenefits: {s.benefits}"
                for s in matched
            )
            sources = [s.name for s in matched]

        else:
            from app.retriever import get_retriever
            retriever = get_retriever(k=10)
            docs = retriever.invoke(f"{question} Maharashtra government scheme")[:10]

            if not docs:
                return {"answer": "No relevant schemes found. Please try rephrasing your query.", "sources": []}

            context = "\n\n".join(doc.page_content for doc in docs)
            sources = [doc.metadata.get("name", "Unknown scheme") for doc in docs]

        prompt = PROMPT_TEMPLATE.format(
            context=context,
            question=question,
            chat_history=chat_history[-2000:]
        )
        model = get_gemini_model()
        response = model.generate_content(prompt)

        return {"answer": response.text, "sources": sources}

    except Exception as e:
        return {
            "answer": "Sorry, I ran into a problem answering that. Please try again in a moment.",
            "sources": [],
        }