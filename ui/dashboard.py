import os

import requests
import streamlit as st
from streamlit_extras.stylable_container import stylable_container

# Use BACKEND_URL from environment, default to localhost for local dev
BACKEND_URL = os.environ.get("BACKEND_URL", "http://app:8000")

st.set_page_config(page_title="LLM Audit Assistant", layout="wide")

with stylable_container(key="header",
                        css_styles="background: #1a2634; color: white; padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem;"):
    st.markdown(
        """
        <h1>🔍 LLM Audit Assistant Dashboard</h1>
        <span style='font-size:1.1rem;'>Secure, self-hosted LLM-powered document analysis for enterprise teams.</span>
        """,
        unsafe_allow_html=True
    )

st.header("📄 Upload Document")
uploaded_file = st.file_uploader("Choose a file (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
if uploaded_file:
    with st.spinner("Uploading and processing..."):
        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
        resp = requests.post(f"{BACKEND_URL}/upload", files=files)
        if resp.status_code == 200:
            st.success(f"Uploaded {uploaded_file.name} ({resp.json().get('chunks', 0)} chunks)")
        else:
            st.error(f"Upload failed: {resp.text}")

st.header("💬 Ask a Question")
question = st.text_input("Enter your question:")
if st.button("Query") and question:
    with st.spinner("Querying LLM..."):
        resp = requests.post(f"{BACKEND_URL}/query", json={"question": question})
        if resp.status_code == 200:
            data = resp.json()
            st.subheader("📝 Answer")
            st.write(data.get("answer", "No answer returned."))
            st.subheader("📚 Source Chunks")
            if data.get("sources"):
                for i, chunk in enumerate(data["sources"]):
                    st.markdown(f"**Chunk {i + 1}:** {chunk['text']}")
            st.subheader("⚙️ Raw Prompt & Token Usage")
            st.write(f"Tokens used: {data.get('tokens_used', 'N/A')}")
        else:
            st.error(f"Error: {resp.text}")
