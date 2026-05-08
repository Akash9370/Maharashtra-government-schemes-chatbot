import streamlit as st
#from app.llm_chain import ask_question
import logging
from app.crud import add_scheme, get_all_schemes, scheme_exists, delete_scheme, update_scheme
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

logging.getLogger().setLevel(logging.ERROR)
logging.getLogger("chromadb").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)

st.set_page_config(page_title="Scheme Chatbot", layout="wide")

# ------------------------
# Custom CSS for UI
# ------------------------
st.markdown("""
<style>

/* =========================
   THEME SUPPORT (AUTO)
   ========================= */

/* Light Mode */
[info-theme="light"] .stApp {
    background-color: #F5F7FA;
}

[info-theme="light"] .user-msg {
    background-color: #DCF8C6;
    color: #000000;
}

[info-theme="light"] .bot-msg {
    background-color: #FFFFFF;
    color: #000000;
}

[info-theme="light"] textarea,
[info-theme="light"] input {
    background-color: #FFFFFF !important;
    color: #000000 !important;
}

/* Dark Mode */
[info-theme="dark"] .stApp {
    background-color: #0E1117;
}

[info-theme="dark"] .user-msg {
    background-color: #A5D6A7;
    color: #000000;
}

[info-theme="dark"] .bot-msg {
    background-color: #262730;
    color: #FFFFFF;
}

[info-theme="dark"] textarea,
[info-theme="dark"] input {
    background-color: #262730 !important;
    color: #FFFFFF !important;
}

/* =========================
   CHAT LAYOUT
   ========================= */

.chat-row {
    display: flex;
    width: 100%;
    margin: 6px 0;
}

.user-row {
    justify-content: flex-end;
}

.bot-row {
    justify-content: flex-start;
}

.user-msg, .bot-msg {
    max-width: 72%;
    padding: 14px 18px;
    border-radius: 18px;
    font-size: 15.5px;
    line-height: 1.55;
    word-wrap: break-word;
    box-shadow: 0 4px 14px rgba(0,0,0,0.18);
}

.user-msg {
    border-bottom-right-radius: 6px;
}

.bot-msg {
    border-bottom-left-radius: 6px;
}

/* =========================
   INPUT BOX FIX
   ========================= */

textarea {
    border-radius: 10px !important;
}

/* Remove red border */
textarea:focus {
    border: 1px solid #888 !important;
    box-shadow: none !important;
}

/* Placeholder */
textarea::placeholder {
    color: #AAAAAA !important;
}

/* =========================
   BUTTONS
   ========================= */

button {
    border-radius: 8px !important;
}

/* =========================
   SIDEBAR
   ========================= */

[info-testid="stSidebar"] {
    background-color: #1E1E1E;
}

/* =========================
   SCROLLBAR
   ========================= */

::-webkit-scrollbar {
    width: 6px;
}

::-webkit-scrollbar-thumb {
    background: #444;
    border-radius: 10px;
}

/* =========================
   SPACING
   ========================= */

.block-container {
    padding-top: 2rem;
}

.hero {
    max-width: 850px;
    margin: 0 auto 20px auto;
    padding: 22px 26px;
    border-radius: 18px;
    background: linear-gradient(135deg, #1F2937, #111827);
    border: 1px solid #374151;
    box-shadow: 0 10px 30px rgba(0,0,0,0.25);
}

.hero h1 {
    margin: 0;
    font-size: 30px;
    color: #FFFFFF;
}

.hero p {
    margin-top: 8px;
    color: #D1D5DB;
    font-size: 15px;
}

.welcome-box {
    max-width: 850px;
    margin: 20px auto;
    padding: 18px 22px;
    border-radius: 16px;
    background-color: #161B22;
    border: 1px solid #30363D;
    color: #E5E7EB;
}

.welcome-box h3 {
    margin-top: 0;
    color: #FFFFFF;
}

.welcome-box p {
    margin: 8px 0;
}

</style>
""", unsafe_allow_html=True)

# ------------------------
# Session State for Chat
# ------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ------------------------
# Sidebar (Admin placeholder)
# ------------------------
# ------------------------
# Sidebar (Admin Panel)
# ------------------------
st.sidebar.title("⚙️ Admin Panel")
st.sidebar.caption("Manage schemes, upload CSVs, and rebuild the knowledge base.")
admin_password = st.sidebar.text_input("Admin Password", type="password")
admin_mode = admin_password == os.getenv("ADMIN_PASSWORD")

if admin_mode:

    # 📊 DB Stats
    schemes = get_all_schemes()
    st.sidebar.write(f"📊 Total Schemes: {len(schemes)}")

    # ------------------------
    # ➕ Add Scheme
    # ------------------------
    with st.sidebar.expander("➕ Add New Scheme"):

        name = st.text_input("Scheme Name")
        description = st.text_area("Description")
        eligibility = st.text_area("Eligibility")
        benefits = st.text_area("Benefits")
        state = st.text_input("State", value="Maharashtra")
        category = st.selectbox(
            "Category",
            ["general", "farmer", "student", "health", "welfare", "women", "housing", "employment", "loan"]
        )

        if st.button("Add Scheme"):
            if name and description:

                if scheme_exists(name):
                    st.warning("⚠️ Scheme already exists in database")
                else:
                    add_scheme({
                        "name": name,
                        "description": description,
                        "eligibility": eligibility,
                        "benefits": benefits,
                        "state": state,
                        "category": category
                    })

                    from app.index_builder import build_index

                    build_index()
                    st.cache_resource.clear()

                    st.success("✅ Scheme added and knowledge base updated")

            else:
                st.warning("Please fill required fields")

    # ------------------------
    # 📤 Bulk Upload Schemes
    # ------------------------
    with st.sidebar.expander("📤 Bulk Upload CSV"):

        uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)

            st.write("Preview:")
            st.dataframe(df.head())

            if st.button("Import CSV Schemes"):
                added = 0
                skipped = 0

                for _, row in df.iterrows():
                    name = str(row.get("name", "")).strip()

                    if not name:
                        skipped += 1
                        continue

                    if scheme_exists(name):
                        skipped += 1
                        continue

                    add_scheme({
                        "name": name,
                        "description": str(row.get("description", "")),
                        "eligibility": str(row.get("eligibility", "")),
                        "benefits": str(row.get("benefits", "")),
                        "state": str(row.get("state", "Maharashtra")),
                        "category": str(row.get("category", "general"))
                    })

                    added += 1

                from app.index_builder import build_index
                build_index()
                st.cache_resource.clear()

                st.success(f"✅ Imported {added} schemes. Skipped {skipped}.")

    # ------------------------
    # 🛠 Manage Schemes
    # ------------------------
    with st.sidebar.expander("🛠 Manage Schemes"):
        schemes = get_all_schemes()

        scheme_options = {
            f"{s.id} - {s.name}": s
            for s in schemes
            if s.name
        }

        selected_label = st.selectbox(
            "Select Scheme",
            list(scheme_options.keys())
        )

        selected_scheme = scheme_options[selected_label]

        new_name = st.text_input("Edit Name", value=selected_scheme.name)
        new_description = st.text_area("Edit Description", value=selected_scheme.description or "")
        new_eligibility = st.text_area("Edit Eligibility", value=selected_scheme.eligibility or "")
        new_benefits = st.text_area("Edit Benefits", value=selected_scheme.benefits or "")
        new_state = st.text_input("Edit State", value=selected_scheme.state or "Maharashtra")
        category_options = ["general", "farmer", "student", "health", "welfare", "women", "housing", "employment",
                            "loan"]

        current_category = selected_scheme.category or "general"

        if current_category not in category_options:
            current_category = "general"

        new_category = st.selectbox(
            "Edit Category",
            category_options,
            index=category_options.index(current_category)
        )

        if st.button("Update Scheme"):
            update_scheme(selected_scheme.id, {
                "name": new_name,
                "description": new_description,
                "eligibility": new_eligibility,
                "benefits": new_benefits,
                "state": new_state,
                "category": new_category
            })

            from app.index_builder import build_index
            build_index()
            st.cache_resource.clear()

            st.success("✅ Scheme updated and index rebuilt")

        if st.button("Delete Scheme"):
            delete_scheme(selected_scheme.id)

            from app.index_builder import build_index
            build_index()
            st.cache_resource.clear()

            st.success("🗑️ Scheme deleted and index rebuilt")
    # ------------------------
    # 🔄 Rebuild Index
    # ------------------------
    with st.sidebar.expander("🔄 Update Knowledge Base"):

        if st.button("Rebuild Index"):
            with st.spinner("Rebuilding index..."):
                from app.index_builder import build_index
                build_index()
            st.success("✅ Index rebuilt successfully")
else:
    st.sidebar.info("Enter admin password to manage schemes")
# ------------------------
# Chat UI
# ------------------------
st.markdown("""
<div class="hero">
    <h1>💬 Maharashtra Scheme Assistant</h1>
    <p>Ask about government schemes for farmers, students, women, housing, health, welfare and more.</p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-box">
        <h3>Try asking:</h3>
        <p>🌾 schemes for farmers</p>
        <p>🎓 scholarships for OBC students</p>
        <p>🏥 health insurance schemes</p>
        <p>🏠 housing schemes in Maharashtra</p>
    </div>
    """, unsafe_allow_html=True)

# ------------------------
# Chat Messages
# ------------------------
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("assistant"):
            st.markdown(msg["content"])

# ------------------------
# Input Area
# ------------------------
user_input = st.chat_input("Ask about Maharashtra government schemes...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    # temporary deployment test
    response = "Test response working"

    st.session_state.messages.append({"role": "bot", "content": response})