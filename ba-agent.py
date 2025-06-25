import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
import os
import pymupdf4llm
import fitz  # PyMuPDF
from PIL import Image
import io
import re
from streamlit_mermaid import st_mermaid

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
    # creates a sidebar table of contents from extracted headings
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
        usage = response.usage_metadata
        token_info = {
            "prompt": usage.prompt_token_count,
            "output": usage.candidates_token_count,
            "total": usage.total_token_count
        }
        return response.text, token_info
    except Exception as e:
        st.error(f"An error occurred during Gemini analysis: {e}")
        return None, None

def generate_mermaid_req_doc(md_text):
    """Generates a technical requirements document in Mermaid.js format."""
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    You are a technical architect. Based on the following business plan, create a technical requirements document using Mermaid.js syntax.
    The document should outline the system architecture, components, and user flow.

    Business Plan (Markdown):
    {md_text}

    IMPORTANT: Your response must contain ONLY the raw Mermaid.js code for the diagram. Do not include any other text, explanations, or markdown code fences like ```mermaid.
    """
    
    try:
        response = model.generate_content(prompt)
        # Clean the response to ensure it's valid Mermaid code
        mermaid_code = response.text
        # The model might still wrap the code in markdown fences. Let's extract it.
        match = re.search(r"```mermaid\n(.*?)\n```", mermaid_code, re.DOTALL)
        if match:
            mermaid_code = match.group(1)
        
        usage = response.usage_metadata
        token_info = {
            "prompt": usage.prompt_token_count,
            "output": usage.candidates_token_count,
            "total": usage.total_token_count
        }
        return mermaid_code.strip(), token_info

    except Exception as e:
        st.error(f"An error occurred during Mermaid diagram generation: {e}")
        return None, None

# --- App Logic with Session State ---

# Initialize session state to store processed data
if "md_text" not in st.session_state:
    st.session_state.md_text = None
    st.session_state.image_list = []
    st.session_state.last_filename = None
    st.session_state.token_counts = {"prompt": 0, "output": 0, "total": 0}
    st.session_state.analysis = None
    st.session_state.mermaid_code = None

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

# 1. Process the file only if it's a new upload
if uploaded_file is not None and uploaded_file.name != st.session_state.last_filename:
    # Reset token counts for the new file session
    st.session_state.token_counts = {"prompt": 0, "output": 0, "total": 0}
    st.session_state.analysis = None
    st.session_state.mermaid_code = None
    st.session_state.last_filename = uploaded_file.name
    temp_pdf_path = "temp_uploaded.pdf"
    try:
        with st.spinner("Processing PDF..."):
            # Write to a temporary file to be processed
            with open(temp_pdf_path, "wb") as f:
                f.write(uploaded_file.getvalue())

            # Extract markdown text and store in session state
            st.session_state.md_text = pymupdf4llm.to_markdown(temp_pdf_path)

            # Extract images and store in session state
            image_list = []
            with fitz.open(temp_pdf_path) as doc:
                for page in doc:
                    images = page.get_images(full=True)
                    for img_index, img in enumerate(images):
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        image = Image.open(io.BytesIO(image_bytes))
                        image_list.append(image)
            st.session_state.image_list = image_list

    except Exception as e:
        st.error("An error occurred while processing the PDF. See details below.")
        st.exception(e)
        # Reset state in case of an error
        st.session_state.md_text = None
        st.session_state.image_list = []
        st.session_state.last_filename = None
        st.session_state.analysis = None
        st.session_state.mermaid_code = None
    finally:
        # Clean up the temporary file immediately after processing
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)

# 2. Display content and analysis button if a file has been successfully processed
if st.session_state.md_text:
    # --- Sidebar ---
    st.sidebar.markdown("## Navigation")
    st.sidebar.markdown("[📄 Extracted Text](#extracted-markdown-text)")
    st.sidebar.markdown("[🖼️ Extracted Images](#extracted-images)")
    st.sidebar.markdown("[🤖 AI Analysis](#gemini-analysis)")
    st.sidebar.markdown("---")

    # Display token usage
    st.sidebar.markdown("## Token Usage")
    st.sidebar.write(f"**Prompt Tokens:** {st.session_state.token_counts['prompt']}")
    st.sidebar.write(f"**Output Tokens:** {st.session_state.token_counts['output']}")
    st.sidebar.write(f"**Total Tokens:** {st.session_state.token_counts['total']}")
    st.sidebar.markdown("---")

    headings = extract_headings(st.session_state.md_text)
    create_sidebar_toc(headings)

    # --- Main Content ---
    st.subheader("Extracted Text", anchor="extracted-markdown-text")
    st.markdown(st.session_state.md_text, unsafe_allow_html=True)

    st.subheader("Extracted Images", anchor="extracted-images")
    if st.session_state.image_list:
        for i, image in enumerate(st.session_state.image_list):
            st.image(image, caption=f"Image {i+1}")
    else:
        st.info("No images found in the PDF.")

    st.subheader("AI Analysis", anchor="gemini-analysis")
    if st.button("Analyze Business Plan"):
        with st.spinner("Analyzing with Gemini..."):
            analysis, token_info = analyze_with_gemini(st.session_state.md_text, st.session_state.image_list)
            if analysis:
                st.session_state.analysis = analysis
                # Update token counts
                st.session_state.token_counts["prompt"] += token_info["prompt"]
                st.session_state.token_counts["output"] += token_info["output"]
                st.session_state.token_counts["total"] += token_info["total"]
                st.rerun()
            else:
                st.error("Analysis failed or returned no content.")

    if st.session_state.analysis:
        st.markdown(st.session_state.analysis)

    st.subheader("Technical Requirements Document", anchor="tech-req-doc")
    if st.button("Generate Technical Requirements Document"):
        with st.spinner("Generating Mermaid.js diagram..."):
            mermaid_code, token_info = generate_mermaid_req_doc(st.session_state.md_text)
            if mermaid_code:
                st.session_state.mermaid_code = mermaid_code
                # Update token counts
                st.session_state.token_counts["prompt"] += token_info["prompt"]
                st.session_state.token_counts["output"] += token_info["output"]
                st.session_state.token_counts["total"] += token_info["total"]
                st.rerun()
            else:
                st.error("Failed to generate Mermaid.js diagram.")

    if st.session_state.mermaid_code:
        st_mermaid(st.session_state.mermaid_code)

# 3. Handle the case where no file is uploaded or it's cleared
if uploaded_file is None and st.session_state.last_filename is not None:
    # If the file is cleared (deselected), reset the state
    st.session_state.md_text = None
    st.session_state.image_list = []
    st.session_state.last_filename = None
    st.session_state.token_counts = {"prompt": 0, "output": 0, "total": 0}
    st.session_state.analysis = None
    st.session_state.mermaid_code = None
    # Rerun to clear the screen
    st.rerun()

if st.session_state.last_filename is None:
    st.info("Please upload a PDF file to begin analysis.")
    st.sidebar.info("Upload a PDF to see the analysis options.")
