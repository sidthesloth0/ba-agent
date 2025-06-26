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
import base64

load_dotenv(override=True)

st.title("PDF Business Plan Analyzer")

# Custom CSS to reduce vertical spacing for a more compact layout
st.markdown("""
<style>
    /* Main container adjustments */
    .main .block-container {
        padding-top: 2rem; /* A bit of space at the top */
    }

    /* Heading adjustments for compactness */
    h1 {
        margin-bottom: 0.5rem !important; /* Space after main title */
    }
    h2, h3 { /* Affects st.subheader and st.header */
        margin-top: 2rem !important; /* Space before section headers */
    }

    /* Sidebar adjustments for compactness */
    [data-testid="stSidebar"] div.stMarkdown {
        padding-top: 0px !important;
        padding-bottom: 0px !important;
    }
    [data-testid="stSidebar"] h2 {
        margin-top: 1rem; /* Space above section headers */
        margin-bottom: 0.25rem; /* Reduce space after sidebar headers */
    }
    /* Custom style for the token display in the sidebar */
    .sidebar-token-usage {
        font-size: 0.9rem;
        color: grey;
        padding: 0px;
        margin-bottom: 0.5rem; /* Reduced bottom margin */
    }
</style>
""", unsafe_allow_html=True)

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

def analyze_with_gemini(md_text, images):
    """Analyzes the business plan text and images using Gemini."""
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    As a business analyst, analyze the provided business plan.
    Provide a concise analysis covering:
    1. Summary
    2. Strengths
    3. Weaknesses
    4. Actionable suggestions
    5. Image analysis

    Business Plan Content:
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
    As a technical architect, create a Mermaid.js diagram from the business plan.
    - Diagram must be top-down (`graph TD`).
    - Outline system architecture, components, and user flow.
    - Output ONLY raw Mermaid.js code.
    - No explanations, markdown fences, custom styles, or link labels.
    - Use basic syntax. Avoid parentheses/brackets in text labels/node text.

    Business Plan:
    {md_text}
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
    st.sidebar.markdown("## Token Usage")
    st.sidebar.markdown(
        f"""
        <div class="sidebar-token-usage">
            <strong>Total:</strong> {st.session_state.token_counts['total']}<br>
            <strong>Prompt:</strong> {st.session_state.token_counts['prompt']}<br>
            <strong>Output:</strong> {st.session_state.token_counts['output']}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown("## Navigation")
    st.sidebar.markdown("[Extracted Text](#extracted-markdown-text)")
    st.sidebar.markdown("[Extracted Images](#extracted-images)")
    st.sidebar.markdown("[AI Analysis](#gemini-analysis)")

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
        # Create the mermaid.live URL with the diagram code
        mermaid_code_bytes = st.session_state.mermaid_code.encode('utf-8')
        base64_bytes = base64.b64encode(mermaid_code_bytes)
        base64_string = base64_bytes.decode('utf-8')
        mermaid_live_url = f"https://mermaid.live/edit#base64:{base64_string}"

        st_mermaid(st.session_state.mermaid_code)

        st.link_button("Open in Mermaid.live", mermaid_live_url)

        with st.expander("View and Copy Mermaid.js Code"):
            st.code(st.session_state.mermaid_code, language="mermaid")
