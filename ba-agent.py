import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
import os
import pymupdf4llm
import fitz  # PyMuPDF
from PIL import Image
import io
# import requests
# import json

load_dotenv(override=True)

st.title("PDF Text Extractor (Markdown)")

gemini_api_key = os.getenv("GOOGLE_API_KEY")
if not gemini_api_key or gemini_api_key.strip() == "":
    st.error("GOOGLE_API_KEY environment variable not found.")
    st.stop()

genai.configure(api_key=gemini_api_key)

def analyze_with_gemini(md_text, images):
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # create content parts starting with text
    content_parts = [f"This is a business plan that has been made. Analyse it and give your opinion on what is good and what needs to be changed or improved: {md_text}"]
    
    # add images directly to content parts
    for img in images:
        content_parts.append(img)
    
    response = model.generate_content(content_parts)
    return response.text

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # save uploaded file to a temporary location
    with open("temp_uploaded.pdf", "wb") as f:
        f.write(uploaded_file.read())
    # extract markdown using pymupdf4llm
    md_text = pymupdf4llm.to_markdown("temp_uploaded.pdf")
    st.subheader("Extracted Markdown Text:")
    st.markdown(md_text, unsafe_allow_html=True)

    # extract images using PyMuPDF
    st.subheader("Extracted Images:")
    doc = fitz.open("temp_uploaded.pdf")
    image_count = 0
    image_list = []
    for page_index in range(len(doc)):
        page = doc[page_index]
        images = page.get_images(full=True)
        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image = Image.open(io.BytesIO(image_bytes))
            st.image(image, caption=f"Page {page_index+1} - Image {img_index+1}")
            image_count += 1
            image_list.append(image)
    if image_count == 0:
        st.info("No images found in the PDF.")
    
    st.subheader("Gemini Analysis")
    if st.button("Analyze with Gemini"):
        with st.spinner("Analyzing with Gemini..."):
            analysis = analyze_with_gemini(md_text, image_list)
            if analysis:
                st.markdown(analysis)
            else:
                st.info("No analysis was returned by Gemini.")
else:
    st.info("Please upload a PDF file to extract its text as markdown.")
