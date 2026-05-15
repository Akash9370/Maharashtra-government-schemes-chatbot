import streamlit as st

st.set_page_config(page_title="Scheme Chatbot", layout="wide")

st.write("✅ streamlit_app.py started")

try:
    st.write("✅ trying to load app.ui")
    from app.ui import *
    st.write("✅ app.ui loaded successfully")
except Exception as e:
    st.error("❌ Error while loading app.ui")
    st.exception(e)