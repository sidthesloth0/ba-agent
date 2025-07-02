import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
import os
import pymupdf4llm
import fitz  # PyMuPDF
from PIL import Image
import io
from streamlit_mermaid import st_mermaid
from extraction_utils import extract_headings, create_sidebar_toc
from gemini_utils import summarize_text, analyze_with_gemini
from docx_utils import generate_mermaid_req_doc, generate_trd_content, create_trd_word_document

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

# --- App Logic with Session State ---

# Initialize session state to store processed data
if "md_text" not in st.session_state:
    st.session_state.md_text = None
    st.session_state.image_list = []
    st.session_state.last_filename = None
    st.session_state.token_counts = {"prompt": 0, "output": 0, "total": 0}
    st.session_state.analysis = None
    st.session_state.mermaid_code = None
    st.session_state.summary = None
    st.session_state.trd_content = None

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

# 1. Process the file only if it's a new upload
if uploaded_file is not None and uploaded_file.name != st.session_state.last_filename:
    # Reset token counts for the new file session
    st.session_state.token_counts = {"prompt": 0, "output": 0, "total": 0}
    st.session_state.analysis = None
    st.session_state.mermaid_code = None
    st.session_state.summary = None
    st.session_state.trd_content = None
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
        st.session_state.summary = None
        st.session_state.trd_content = None
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

    # --- Summarization Section ---
    st.subheader("Token Optimization: Summary")
    if st.button("Generate Summary"):
        with st.spinner("Generating summary..."):
            summary, token_info = summarize_text(st.session_state.md_text)
            if summary and token_info:
                st.session_state.summary = summary
                # Update token counts
                st.session_state.token_counts["prompt"] += token_info["prompt"]
                st.session_state.token_counts["output"] += token_info["output"]
                st.session_state.token_counts["total"] += token_info["total"]
                st.rerun()

    if st.session_state.summary:
        st.markdown("### Generated Summary")
        with st.container(height=200):
            st.markdown(st.session_state.summary)

    # --- Analysis and TRD Section ---
    st.subheader("AI Analysis & Technical Document Generation", anchor="gemini-analysis")

    use_summary = False
    if st.session_state.summary:
        use_summary = st.checkbox("Use generated summary for analysis and TRD", value=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Analyze Business Plan"):
            with st.spinner("Analyzing with Gemini..."):
                input_text = st.session_state.summary if use_summary else st.session_state.md_text
                images_to_analyze = [] if use_summary else st.session_state.image_list
                
                analysis, token_info = analyze_with_gemini(input_text, images_to_analyze)
                if analysis and token_info:
                    st.session_state.analysis = analysis
                    # Update token counts
                    st.session_state.token_counts["prompt"] += token_info["prompt"]
                    st.session_state.token_counts["output"] += token_info["output"]
                    st.session_state.token_counts["total"] += token_info["total"]
                    st.rerun()

    with col2:
        if st.button("Generate Technical Requirements Document"):
            with st.spinner("Generating Technical Requirements Document... This may take a moment."):
                input_text = st.session_state.summary if use_summary else st.session_state.md_text
                
                # Generate Mermaid Diagram
                mermaid_code, mermaid_token_info = generate_mermaid_req_doc(input_text)
                
                # Generate TRD Content
                trd_content, trd_token_info = generate_trd_content(input_text)

                if mermaid_code and mermaid_token_info and trd_content and trd_token_info:
                    st.session_state.mermaid_code = mermaid_code
                    st.session_state.trd_content = trd_content
                    
                    # Update token counts by aggregating both calls
                    st.session_state.token_counts["prompt"] += mermaid_token_info["prompt"] + trd_token_info["prompt"]
                    st.session_state.token_counts["output"] += mermaid_token_info["output"] + trd_token_info["output"]
                    st.session_state.token_counts["total"] += mermaid_token_info["total"] + trd_token_info["total"]
                    
                    st.rerun()

    if st.session_state.analysis:
        st.markdown("### Business Analysis")
        st.markdown(st.session_state.analysis)

    if st.session_state.mermaid_code and st.session_state.trd_content:
        st.markdown("### Technical Requirements Document")
        st.success("Technical Requirements Document generated successfully!")
        
        # Display TRD content
        with st.expander("View Generated TRD Content", expanded=True):
            st.markdown(st.session_state.trd_content)

        # Render the diagram in the app
        st.markdown("#### System Architecture Diagram")
        st_mermaid(st.session_state.mermaid_code)

        doc_stream = create_trd_word_document(st.session_state.trd_content, st.session_state.mermaid_code)

        if doc_stream:
            st.download_button(
                label="Download Full TRD (Word Document)",
                data=doc_stream,
                file_name="Technical_Requirements_Document.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

        with st.expander("View and Copy Mermaid.js Code"):
            st.code(st.session_state.mermaid_code, language="mermaid")
