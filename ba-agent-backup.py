# ba agent using openai framework; deprecated - using ba-agent.py instead
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import json, os, requests, pymupdf4llm
import fitz  # PyMuPDF
from PIL import Image
import io


st.title("PDF Text Extractor (Markdown)")

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
    if image_count == 0:
        st.info("No images found in the PDF.")
else:
    st.info("Please upload a PDF file to extract its text as markdown.")


client = OpenAI()
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    st.error("GOOGLE_API_KEY environment variable not found.")
    st.stop()

st.subheader("Gemini Analysis")
def analyze_with_gemini(md_text):
    client = OpenAI(
        api_key=google_api_key,
        api_base="https://generativelanguage.googleapis.com"
    )
    messages = [{
        "role": "user",
        "content": f"This is a business plan that has been made. \
            Analyse it and give your opinion on what is good and what needs to be changed or improved: {md_text}"
    }]
    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages = messages
    )
    return response.choices[0].message.content

if uploaded_file is not None:
    if st.button("Analyze with Gemini"):
        st.subheader("Message Sent to Gemini:")
        st.markdown(f"> {md_text}")
        response = analyze_with_gemini(md_text)
        st.subheader("Gemini's Response:")
        st.markdown(response)