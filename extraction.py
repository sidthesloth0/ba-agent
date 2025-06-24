import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import json, os, requests, pymupdf4llm


st.title("PDF Text Extractor (Markdown)")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Save uploaded file to a temporary location
    with open("temp_uploaded.pdf", "wb") as f:
        f.write(uploaded_file.read())
    # Extract markdown using pymupdf4llm
    md_text = pymupdf4llm.to_markdown("temp_uploaded.pdf")
    st.subheader("Extracted Markdown Text:")
    st.markdown(md_text, unsafe_allow_html=True)
else:
    st.info("Please upload a PDF file to extract its text as markdown.")
