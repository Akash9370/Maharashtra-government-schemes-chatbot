# Maharashtra Government Schemes Chatbot

A conversational AI chatbot built to help users explore Maharashtra government schemes in a simple and user-friendly way.

The project combines semantic search, vector embeddings, a dynamic admin panel, and Google Gemini to provide scheme recommendations based on natural language questions.

Instead of searching manually through government portals, users can ask questions like:

- "Schemes for farmers"
- "Scholarships for OBC students"
- "Housing schemes in Maharashtra"
- "Health insurance schemes"

and receive structured answers instantly.

---

# Features

## User Features

- Conversational chatbot interface
- Natural language scheme search
- Semantic retrieval using embeddings
- Category-aware scheme filtering
- Multi-scheme structured responses
- Responsive Streamlit UI
- Chat history support
- Light/Dark mode support

## Admin Features

- Password-protected admin panel
- Add new schemes manually
- Bulk CSV upload
- Edit existing schemes
- Delete schemes
- Automatic ChromaDB rebuild after updates
- Duplicate prevention

---

# Tech Stack

| Layer           | Technology                                                  |
| --------------- | ----------------------------------------------------------- |
| Frontend        | Streamlit                                                   |
| Backend         | Python                                                      |
| LLM             | Google Gemini                                               |
| Vector Database | ChromaDB                                                    |
| Embeddings      | sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 |
| Database        | SQLite                                                      |
| ORM             | SQLAlchemy                                                  |
| AI Framework    | LangChain                                                   |

---

# Project Architecture

```text
┌─────────────────────┐
│     Streamlit UI    │
│  Chat + Admin Panel │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    llm_chain.py     │
│ Query Routing Logic │
└──────────┬──────────┘
           │
 ┌─────────┴─────────┐
 │                   │
 ▼                   ▼
Category Route    Semantic Route
(DB Filtering)    (Vector Search)
 │                   │
 ▼                   ▼
SQLite DB         ChromaDB
(SQLAlchemy)      (Embeddings)
 │                   │
 └─────────┬─────────┘
           ▼
   Context Construction
           ▼
┌─────────────────────┐
│    Google Gemini    │
│   Response Generation│
└──────────┬──────────┘
           ▼
      Final Response
```

---

# How It Works

## 1. User Query

The user enters a natural language question in the Streamlit chatbot.

Example:

```text
Schemes for farmers
```

---

## 2. Query Classification

The system first detects whether the query belongs to a specific category such as:

- farmer
- student
- health
- welfare
- housing
- women
- employment
- loan

If a category is detected, the chatbot directly filters relevant schemes from the database.

If no category is detected, semantic vector retrieval is used.

---

## 3. Semantic Search

For general or conversational queries, the chatbot uses:

- HuggingFace multilingual embeddings
- Chroma vector database
- LangChain retriever

This helps match semantically similar schemes even if the exact keywords are not present.

---

## 4. Response Generation

Relevant schemes are passed to Gemini along with a strict prompt.

Gemini formats the final answer into clean readable scheme lists.

---

# Database Structure

Each scheme contains:

| Column      | Description                 |
| ----------- | --------------------------- |
| name        | Scheme name                 |
| description | Detailed scheme description |
| eligibility | Eligibility criteria        |
| benefits    | Benefits provided           |
| state       | State name                  |
| category    | Scheme category             |

---

# Folder Structure

```text
schemeresume/
│
├── app/
│   ├── __init__.py
│   ├── api.py
│   ├── crud.py
│   ├── db.py
│   ├── embeddings.py
│   ├── index_builder.py
│   ├── llm_chain.py
│   ├── models.py
│   ├── retriever.py
│   └── ui.py
│
├── info/
│   ├── chroma_db/
│   └── Scheme.csv
│
├── scripts/
│   ├── check_duplicates.py
│   └── cleanup_db.py
│
├── migrate_csv_to_db.py
├── rebuild_chroma_from_db.py
├── requirements.txt
├── .env
└── README.md
```

---

# Running the Project

## 1. Clone Repository

```bash
git clone <repository-url>
cd schemeresume
```

---

## 2. Create Virtual Environment

```bash
python -m venv .venv
```

Activate:

### Windows

```bash
.venv\Scripts\activate
```

---

## 3. Install Requirements

```bash
pip install -r requirements.txt
```

---

## 4. Setup Environment Variables

Create `.env`

```env
GOOGLE_API_KEY=your_api_key
HF_TOKEN=your_huggingface_token
ADMIN_PASSWORD=your_admin_password
```

---

## 5. Build Vector Index

```bash
python -m app.index_builder
```

---

## 6. Run Streamlit

```bash
python -m streamlit run app/ui.py
```

---

# Challenges Faced During Development

Some real development challenges faced during the project:

- Resolving LangChain version mismatches between \`langchain\`, \`langchain-community\`, and \`langchain-core\`
- Migration issues caused by changing LangChain imports and deprecated modules
- ChromaDB deprecation warnings and package migration handling
- Google Gemini API version/model compatibility issues
- Free-tier Gemini API rate limits during testing
- Dependency conflicts involving \`protobuf\`, \`grpcio-status\`, and Google AI packages
- HuggingFace authentication and caching warnings on Windows
-  FAISS deserialization security warnings during local vector loading
-  Streamlit \`ScriptRunContext\` warnings caused by incorrect execution method
-  Circular import issues between retriever and LLM modules
-  Dynamic ChromaDB rebuilding after admin updates
-  Cleaning duplicate and inconsistent government scheme data
-  Balancing semantic retrieval with category-based filtering
-  Improving retrieval relevance for conversational queries
-  Maintaining consistent categories across manually added and CSV-imported schemes
-  Python package import/path issues inside modular project structure
-  SQLite table initialization and migration problems during early development

---

# Future Improvements

Planned improvements:

- Marathi/Hindi translation support
- Voice-based queries
- Official government API integration
- Better ranking/reranking pipeline
- Deployment on cloud platform
- Advanced analytics dashboard
- OCR support for government PDFs
- Scheme recommendation personalization

---

# Resume Highlights

This project demonstrates:

- Retrieval-Augmented Generation (RAG)
- Semantic search systems
- Vector databases
- LangChain integration
- LLM application development
- Full-stack AI project architecture
- Database management
- Streamlit frontend development
- Prompt engineering
- Dynamic knowledge base updates

---

# Author

Akash Gaikwad

Built as a resume and learning project focused on practical AI application development using modern LLM and vector search workflows.

