import streamlit as st
from app.crud import add_scheme, get_all_schemes, scheme_exists, delete_scheme, update_scheme
import os
from dotenv import load_dotenv
import pandas as pd
import gc

load_dotenv()

st.set_page_config(page_title="Scheme Chatbot", layout="wide")

st.title("💬 Maharashtra Scheme Assistant")
st.write("Ask about Maharashtra government schemes.")

# ------------------------
# Admin Login
# ------------------------
st.sidebar.title("⚙️ Admin Panel")

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

admin_password = st.sidebar.text_input("Admin Password", type="password")

if st.sidebar.button("Login"):
    if admin_password == os.getenv("ADMIN_PASSWORD"):
        st.session_state.admin_logged_in = True
    else:
        st.sidebar.error("Wrong password")

if st.session_state.admin_logged_in:
    st.sidebar.success("✅ Admin login worked")
    schemes = get_all_schemes()
    st.sidebar.write(f"📊 Total Schemes: {len(schemes)}")

    if st.sidebar.button("🔄 Rebuild Knowledge Base"):
        st.sidebar.warning(
            "Stop the app and run: python -m app.index_builder"
        )
    with st.sidebar.expander("🔍 Check Database"):
        search_text = st.text_input("Search scheme in DB")

        if search_text:
            schemes = get_all_schemes()

            matches = [
                s for s in schemes
                if search_text.lower() in s.name.lower()
            ]

            st.write(f"Found {len(matches)} matching schemes")

            for s in matches:
                st.markdown(f"""
                **Scheme Name:** {s.name}

                **Description:** {s.description}

                **Eligibility:** {s.eligibility}

                **Benefits:** {s.benefits}

                **Category:** {s.category}
                ---
                """)

    with st.sidebar.expander("🛠 Manage Schemes"):
        schemes = get_all_schemes()

        scheme_options = {
            f"{s.id} - {s.name}": s
            for s in schemes
            if s.name
        }

        if not scheme_options:
            st.info("No schemes found.")
        else:
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

            category_options = [
                "general", "farmer", "student", "health", "welfare",
                "women", "housing", "employment", "loan"
            ]

            current_category = selected_scheme.category or "general"
            if current_category not in category_options:
                current_category = "general"

            new_category = st.selectbox(
                "Edit Category",
                category_options,
                index=category_options.index(current_category)
            )

            if st.button("Update Scheme"):

                success = update_scheme(selected_scheme.id, {
                    "name": new_name,
                    "description": new_description,
                    "eligibility": new_eligibility,
                    "benefits": new_benefits,
                    "state": new_state,
                    "category": new_category
                })

                if success:
                    with st.spinner("Updating knowledge base..."):
                        try:
                            from app.retriever import get_retriever
                            import gc
                            from app.index_builder import build_index
                            get_retriever.clear()
                            gc.collect()
                            build_index()
                            st.success("✅ Knowledge base updated")
                        except Exception as e:
                            st.error(f"Failed to update knowledge base: {e}")
                else:
                    st.error("❌ Scheme update failed")

            if st.button("Delete Scheme"):

                success = delete_scheme(selected_scheme.id)

                if success:
                    with st.spinner("Updating knowledge base..."):
                        try:
                            from app.index_builder import delete_scheme_from_index

                            delete_scheme_from_index(name)
                            st.success("✅ Knowledge base updated")
                        except Exception as e:
                            st.error(f"Failed to update knowledge base: {e}")
                else:
                        st.error("❌ Scheme delete failed")


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

                    with st.spinner("Updating knowledge base..."):
                        try:
                            from app.index_builder import add_scheme_to_index

                            new_scheme = next((s for s in get_all_schemes() if s.name == name), None)
                            if new_scheme:
                                add_scheme_to_index(new_scheme)
                            st.success("✅ Knowledge base updated")
                        except Exception as e:
                            st.error(f"Failed to update knowledge base: {e}")

                    st.cache_resource.clear()

                    st.success("✅ Scheme added to database")
            else:
                st.warning("Please fill Scheme Name and Description")

        with st.sidebar.expander("📤 Bulk Upload CSV"):
            uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

            if uploaded_file is not None:
                try:
                    df = pd.read_csv(uploaded_file)
                except Exception as e:
                    st.error(f"Couldn't read that CSV file: {e}")
                    df = None

                if df is not None:
                    st.write("Preview:")
                    st.dataframe(df.head())

                    required_columns = ["name", "description", "eligibility", "benefits"]
                    missing_columns = [col for col in required_columns if col not in df.columns]

                    if missing_columns:
                        st.error(f"Missing columns: {missing_columns}")
                    else:
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

                            st.success(f"✅ Imported {added} schemes. Skipped {skipped}.")

                            with st.spinner("Updating knowledge base..."):
                                try:
                                    from app.retriever import get_retriever
                                    import gc

                                    get_retriever.clear()
                                    gc.collect()
                                    build_index()
                                    st.success("✅ Knowledge base updated")
                                except Exception as e:
                                    st.error(f"Failed to update knowledge base: {e}")


else:
    st.sidebar.info("Enter admin password")

# ------------------------
# Chat State
# ------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ------------------------
# Show Messages
# ------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ------------------------
# Chat Input
# ------------------------
user_input = st.chat_input("Ask about Maharashtra government schemes...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    from app.llm_chain import ask_question

    with st.spinner("Searching schemes..."):
        result = ask_question(user_input)

    if isinstance(result, dict):
        response = result.get("answer", "Sorry, I could not find an answer.")
    else:
        response = result

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()