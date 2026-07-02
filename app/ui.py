import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

st.title("💬 Maharashtra Scheme Assistant")

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
else:
    st.sidebar.info("Enter admin password")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask about Maharashtra government schemes...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.messages.append({"role": "assistant", "content": "Test response working"})
    st.rerun()