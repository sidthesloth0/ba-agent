import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
import os
import pymupdf4llm
import fitz  # PyMuPDF
from PIL import Image
import io
import re

load_dotenv(override=True)

st.title("PDF Business Plan Analyzer")

gemini_api_key = os.getenv("GOOGLE_API_KEY")
if not gemini_api_key or gemini_api_key.strip() == "":
    st.error("GOOGLE_API_KEY environment variable not found.")
    st.stop()

genai.configure(api_key=gemini_api_key)

def extract_headings(markdown_text):
    """Extracts headings from markdown text for a table of contents."""
    headings = []
    for line in markdown_text.split('\n'):
        match = re.match(r'^(#{1,6})\s+(.+)', line.strip())
        if match:
            level = len(match.group(1))
            title = match.group(2).strip()
            anchor_id = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '-').lower()
            headings.append({'level': level, 'title': title, 'anchor': anchor_id})
    return headings

def create_sidebar_toc(headings):
    """Creates a sidebar table of contents from extracted headings."""
    if headings:
        st.sidebar.markdown("## Table of Contents")
        for heading in headings:
            indent = "  " * (heading['level'] - 1)
            st.sidebar.markdown(f"{indent}- [{heading['title']}](#{heading['anchor']})")
        st.sidebar.markdown("---")

def analyze_with_gemini(md_text, images):
    """Analyzes the business plan text and images using Gemini."""
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    You are an expert business analyst.
    Analyze the following business plan, which has been extracted from a PDF.
    The plan is provided in Markdown format, followed by any images from the document.

    Your analysis should cover the following points:
    1.  **Overall Summary:** Briefly summarize the business plan.
    2.  **Strengths:** Identify the strong points of the plan. What is well-thought-out? What are the competitive advantages?
    3.  **Weaknesses:** Identify the weak points. Are there any gaps in the plan? What are the potential risks?
    4.  **Suggestions for Improvement:** Provide actionable suggestions to improve the business plan. Be specific.
    5.  **Image Analysis:** If there are images, analyze them in the context of the business plan. Do they support the text? Are they effective?

    Here is the business plan content:

    **Text (Markdown):**
    {md_text}
    """
    
    content_parts = [prompt]
    
    if images:
        content_parts.append("\n**Images:**")
        for img in images:
            content_parts.append(img)
    
    try:
        response = model.generate_content(content_parts)
        return response.text
    except Exception as e:
        st.error(f"An error occurred during Gemini analysis: {e}")
        return None

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    temp_pdf_path = "temp_uploaded.pdf"
    try:
        # Write uploaded content to the temporary file
        with open(temp_pdf_path, "wb") as f:
            f.write(uploaded_file.getvalue())

        # Extract markdown text using pymupdf4llm
        md_text = pymupdf4llm.to_markdown(temp_pdf_path)

        # Extract images using PyMuPDF from the same file
        image_list = []
        with fitz.open(temp_pdf_path) as doc:
            for page_num, page in enumerate(doc):
                images = page.get_images(full=True)
                for img_index, img in enumerate(images):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image = Image.open(io.BytesIO(image_bytes))
                    image_list.append(image)

        # --- Sidebar ---
        st.sidebar.markdown("## Navigation")
        st.sidebar.markdown("[📄 Extracted Text](#extracted-markdown-text)")
        st.sidebar.markdown("[🖼️ Extracted Images](#extracted-images)")
        st.sidebar.markdown("[🤖 AI Analysis](#gemini-analysis)")
        st.sidebar.markdown("---")

        headings = extract_headings(md_text)
        create_sidebar_toc(headings)

        # --- Main Content ---
        st.subheader("Extracted Text", anchor="extracted-markdown-text")
        st.markdown(md_text, unsafe_allow_html=True)

        st.subheader("Extracted Images", anchor="extracted-images")
        if image_list:
            for i, image in enumerate(image_list):
                st.image(image, caption=f"Image {i+1}")
        else:
            st.info("No images found in the PDF.")

        st.subheader("AI Analysis", anchor="gemini-analysis")
        with st.spinner("Analyzing with Gemini..."):
            analysis = analyze_with_gemini(md_text, image_list)
            if analysis:
                st.markdown(analysis)
            else:
                st.error("Analysis failed or returned no content.")

    except Exception as e:
        st.error("An error occurred while processing the PDF. See details below.")
        st.exception(e)
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)

else:
    st.info("Please upload a PDF file to begin analysis.")
    st.sidebar.info("Upload a PDF to see the analysis options.")
