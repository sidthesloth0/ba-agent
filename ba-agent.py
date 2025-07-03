import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
import os
import pymupdf4llm
import fitz  # PyMuPDF
from PIL import Image
import io
import gc
from streamlit_mermaid import st_mermaid
from gemini_utils import (
    analyze_with_gemini,
    summarize_text,
    generate_mermaid_req_doc,
    generate_trd_content
)
from docx_utils import create_trd_word_document

load_dotenv(override=True)

st.title("📄 Business Analysis Agent")
st.markdown("Powered by Google Gemini")

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
    [data-testid="stSidebar"] ul {
        list-style-type: none;
        padding-left: 0;
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

# Initialize session state
if "files" not in st.session_state:
    st.session_state.files = {}  # Dictionary to hold data for each file
if "token_counts" not in st.session_state:
    st.session_state.token_counts = {"prompt": 0, "output": 0, "total": 0}
if "global_analysis" not in st.session_state:
    st.session_state.global_analysis = {
        "summary": None,
        "analysis": None,
        "mermaid_code": None,
        "trd_content": None,
        "use_summary": False
    }

uploaded_files = st.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True)

# 1. Process uploaded files
if uploaded_files:
    for uploaded_file in uploaded_files:
        # Process only new files that haven't been processed yet
        if uploaded_file.name not in st.session_state.files:
            temp_pdf_path = f"temp_{uploaded_file.name}"
            try:
                with st.spinner(f"Processing {uploaded_file.name}..."):
                    # Write to a temporary file to be processed
                    with open(temp_pdf_path, "wb") as f:
                        f.write(uploaded_file.getvalue())

                    # Extract markdown text and store in session state
                    md_text = pymupdf4llm.to_markdown(temp_pdf_path)

                    # Extract images and store in session state
                    image_list = []
                    doc = fitz.open(temp_pdf_path)
                    for page in doc:
                        images = page.get_images(full=True)
                        for img_index, img in enumerate(images):
                            xref = img[0]
                            base_image = doc.extract_image(xref)
                            image_bytes = base_image["image"]
                            image = Image.open(io.BytesIO(image_bytes))
                            image_list.append(image)
                    doc.close()
                    gc.collect()  # Force garbage collection to release file lock

                    # Store extracted data in session state under the file's name
                    st.session_state.files[uploaded_file.name] = {
                        "md_text": md_text,
                        "image_list": image_list,
                        "summary": None,
                        "analysis": None,
                        "mermaid_code": None,
                        "trd_content": None,
                        "use_summary": False  # Default to not using summary
                    }

            except Exception as e:
                st.error(f"An error occurred while processing {uploaded_file.name}.")
                st.exception(e)
            finally:
                # Clean up the temporary file immediately after processing
                if os.path.exists(temp_pdf_path):
                    os.remove(temp_pdf_path)

# --- Sidebar ---
with st.sidebar:
    st.markdown("## Token Usage")
    st.markdown(
        f"""
        <div class="sidebar-token-usage">
            <strong>Total:</strong> {st.session_state.token_counts['total']}<br>
            <strong>Prompt:</strong> {st.session_state.token_counts['prompt']}<br>
            <strong>Output:</strong> {st.session_state.token_counts['output']}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.markdown("## Navigation")
    st.markdown("- [Batch Actions](#batch-actions)")
    if st.session_state.files:
        st.markdown("### Processed Files")
        for file_name in st.session_state.files.keys():
            anchor_link = file_name.replace(' ', '-').replace('.', '-')
            st.markdown(f"- [{file_name}](#{anchor_link})")

# --- Main Content ---
if not st.session_state.files:
    st.info("Upload one or more PDF files to begin analysis.")
else:
    # --- Batch Action Buttons ---
    st.markdown("<a name='batch-actions'></a>", unsafe_allow_html=True)
    st.subheader("Batch Actions")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Generate All Summaries", key="summarize_all_top"):
            with st.spinner("Generating all summaries..."):
                for file_name, file_data in st.session_state.files.items():
                    if not file_data["summary"]:
                        summary, token_info = summarize_text(file_data["md_text"], file_data["image_list"])
                        if summary and token_info:
                            file_data["summary"] = summary
                            st.session_state.token_counts["prompt"] += token_info["prompt"]
                            st.session_state.token_counts["output"] += token_info["output"]
                            st.session_state.token_counts["total"] += token_info["total"]
                st.rerun()
    with col2:
        if st.button("Analyze All Business Plans", key="analyze_all_top"):
            with st.spinner("Analyzing all business plans..."):
                for file_name, file_data in st.session_state.files.items():
                    if not file_data["analysis"]:
                        input_text = file_data["summary"] if file_data.get("use_summary", False) else file_data["md_text"]
                        images_to_analyze = [] if file_data.get("use_summary", False) else file_data["image_list"]
                        analysis, token_info = analyze_with_gemini(input_text, images_to_analyze)
                        if analysis and token_info:
                            file_data["analysis"] = analysis
                            st.session_state.token_counts["prompt"] += token_info["prompt"]
                            st.session_state.token_counts["output"] += token_info["output"]
                            st.session_state.token_counts["total"] += token_info["total"]
                st.rerun()
    with col3:
        if st.button("Generate All TRDs", key="trd_all_top"):
            with st.spinner("Generating all TRDs..."):
                for file_name, file_data in st.session_state.files.items():
                    if not file_data["trd_content"]:
                        input_text = file_data["summary"] if file_data.get("use_summary", False) else file_data["md_text"]
                        images_to_analyze = [] if file_data.get("use_summary", False) else file_data["image_list"]
                        mermaid_code, mermaid_token_info = generate_mermaid_req_doc(input_text, images_to_analyze)
                        trd_content, trd_token_info = generate_trd_content(input_text, images_to_analyze)
                        if mermaid_code and trd_content:
                            file_data["mermaid_code"] = mermaid_code
                            file_data["trd_content"] = trd_content
                            st.session_state.token_counts["prompt"] += mermaid_token_info["prompt"] + trd_token_info["prompt"]
                            st.session_state.token_counts["output"] += mermaid_token_info["output"] + trd_token_info["output"]
                            st.session_state.token_counts["total"] += mermaid_token_info["total"] + trd_token_info["total"]
                st.rerun()

    st.divider()

    # --- Global Batch Actions ---
    if len(st.session_state.files) > 1:
        st.subheader("Global Batch Actions (All Files Combined)")
        
        # Combine all text and images for global analysis
        combined_text = "\n\n--- \n\n".join([data["md_text"] for data in st.session_state.files.values()])
        combined_images = [img for data in st.session_state.files.values() for img in data["image_list"]]

        g_col1, g_col2, g_col3 = st.columns(3)
        with g_col1:
            if st.button("Generate Global Summary", key="summarize_global"):
                with st.spinner("Generating global summary..."):
                    summary, token_info = summarize_text(combined_text, combined_images)
                    if summary and token_info:
                        st.session_state.global_analysis["summary"] = summary
                        st.session_state.token_counts["prompt"] += token_info["prompt"]
                        st.session_state.token_counts["output"] += token_info["output"]
                        st.session_state.token_counts["total"] += token_info["total"]
                        st.rerun()
        
        with g_col2:
            if st.button("Analyze Global Business Plan", key="analyze_global"):
                with st.spinner("Analyzing global business plan..."):
                    use_global_summary = st.session_state.global_analysis.get("use_summary", False)
                    input_text = st.session_state.global_analysis["summary"] if use_global_summary and st.session_state.global_analysis["summary"] else combined_text
                    images_to_analyze = [] if use_global_summary else combined_images
                    
                    analysis, token_info = analyze_with_gemini(input_text, images_to_analyze)
                    if analysis and token_info:
                        st.session_state.global_analysis["analysis"] = analysis
                        st.session_state.token_counts["prompt"] += token_info["prompt"]
                        st.session_state.token_counts["output"] += token_info["output"]
                        st.session_state.token_counts["total"] += token_info["total"]
                        st.rerun()

        with g_col3:
            if st.button("Generate Global TRD", key="trd_global"):
                with st.spinner("Generating global TRD..."):
                    use_global_summary = st.session_state.global_analysis.get("use_summary", False)
                    input_text = st.session_state.global_analysis["summary"] if use_global_summary and st.session_state.global_analysis["summary"] else combined_text
                    images_to_analyze = [] if use_global_summary else combined_images

                    mermaid_code, mermaid_token_info = generate_mermaid_req_doc(input_text, images_to_analyze)
                    trd_content, trd_token_info = generate_trd_content(input_text, images_to_analyze)

                    if mermaid_code and trd_content:
                        st.session_state.global_analysis["mermaid_code"] = mermaid_code
                        st.session_state.global_analysis["trd_content"] = trd_content
                        st.session_state.token_counts["prompt"] += mermaid_token_info["prompt"] + trd_token_info["prompt"]
                        st.session_state.token_counts["output"] += mermaid_token_info["output"] + trd_token_info["output"]
                        st.session_state.token_counts["total"] += mermaid_token_info["total"] + trd_token_info["total"]
                        st.rerun()

        # --- Display Global Analysis Results ---
        if st.session_state.global_analysis["summary"] or st.session_state.global_analysis["analysis"] or st.session_state.global_analysis["trd_content"]:
            st.markdown("### Global Analysis Results")

            if st.session_state.global_analysis["summary"]:
                st.session_state.global_analysis["use_summary"] = st.checkbox(
                    "Use global summary for analysis and TRD",
                    value=st.session_state.global_analysis.get("use_summary", True),
                    key="use_global_summary"
                )
                st.markdown("#### Global Summary")
                with st.container(height=200):
                    st.markdown(st.session_state.global_analysis["summary"])

            if st.session_state.global_analysis["analysis"]:
                st.markdown("#### Global Business Analysis")
                st.markdown(st.session_state.global_analysis["analysis"])

            if st.session_state.global_analysis["mermaid_code"] and st.session_state.global_analysis["trd_content"]:
                st.markdown("#### Global Technical Requirements Document")
                with st.expander("View Global TRD Content", expanded=False):
                    st.markdown(st.session_state.global_analysis["trd_content"])
                
                st.markdown("##### Global System Architecture Diagram")
                st_mermaid(st.session_state.global_analysis["mermaid_code"], key="global_mermaid")

                doc_stream = create_trd_word_document(st.session_state.global_analysis["trd_content"], st.session_state.global_analysis["mermaid_code"])
                if doc_stream:
                    st.download_button(
                        label="Download Global TRD (Word Document)",
                        data=doc_stream,
                        file_name="TRD_Global.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key="download_global_trd"
                    )
        st.divider()


    # --- File-Specific Analysis ---
    for file_name, file_data in st.session_state.files.items():
        anchor_link = file_name.replace(' ', '-').replace('.', '-')
        st.markdown(f"<a name='{anchor_link}'></a>", unsafe_allow_html=True)
        st.header(f"Analysis for: {file_name}")

        with st.expander("Extracted Content", expanded=False):
            st.subheader("Extracted Text")
            st.markdown(file_data["md_text"], unsafe_allow_html=True)

            st.subheader("Extracted Images")
            if file_data["image_list"]:
                for i, image in enumerate(file_data["image_list"]):
                    st.image(image, caption=f"Image {i+1}")
            else:
                st.info("No images found in this PDF.")

        # --- Summarization Section ---
        st.subheader("Token Optimization: Summary")
        if st.button(f"Generate Summary for {file_name}", key=f"summary_{file_name}"):
            with st.spinner("Generating summary..."):
                summary, token_info = summarize_text(file_data["md_text"], file_data["image_list"])
                if summary and token_info:
                    file_data["summary"] = summary
                    st.session_state.token_counts["prompt"] += token_info["prompt"]
                    st.session_state.token_counts["output"] += token_info["output"]
                    st.session_state.token_counts["total"] += token_info["total"]
                    st.rerun()

        if file_data["summary"]:
            st.markdown("### Generated Summary")
            with st.container(height=200):
                st.markdown(file_data["summary"])

        # --- Analysis and TRD Section ---
        st.subheader("AI Analysis & Technical Document Generation")

        if file_data["summary"]:
            file_data["use_summary"] = st.checkbox(
                "Use generated summary for analysis and TRD",
                value=file_data.get("use_summary", True),
                key=f"use_summary_{file_name}"
            )

        col1, col2 = st.columns(2)

        with col1:
            if st.button(f"Analyze Business Plan for {file_name}", key=f"analyze_{file_name}"):
                with st.spinner("Analyzing with Gemini..."):
                    input_text = file_data["summary"] if file_data["use_summary"] else file_data["md_text"]
                    images_to_analyze = [] if file_data["use_summary"] else file_data["image_list"]

                    analysis, token_info = analyze_with_gemini(input_text, images_to_analyze)
                    if analysis and token_info:
                        file_data["analysis"] = analysis
                        st.session_state.token_counts["prompt"] += token_info["prompt"]
                        st.session_state.token_counts["output"] += token_info["output"]
                        st.session_state.token_counts["total"] += token_info["total"]
                        st.rerun()

        with col2:
            if st.button(f"Generate TRD for {file_name}", key=f"trd_{file_name}"):
                with st.spinner("Generating Technical Requirements Document..."):
                    input_text = file_data["summary"] if file_data["use_summary"] else file_data["md_text"]
                    images_to_analyze = [] if file_data["use_summary"] else file_data["image_list"]

                    mermaid_code, mermaid_token_info = generate_mermaid_req_doc(input_text, images_to_analyze)
                    trd_content, trd_token_info = generate_trd_content(input_text, images_to_analyze)

                    if mermaid_code and trd_content:
                        file_data["mermaid_code"] = mermaid_code
                        file_data["trd_content"] = trd_content
                        st.session_state.token_counts["prompt"] += mermaid_token_info["prompt"] + trd_token_info["prompt"]
                        st.session_state.token_counts["output"] += mermaid_token_info["output"] + trd_token_info["output"]
                        st.session_state.token_counts["total"] += mermaid_token_info["total"] + trd_token_info["total"]
                        st.rerun()

        if file_data["analysis"]:
            st.markdown("### Business Analysis")
            st.markdown(file_data["analysis"])

        if file_data["mermaid_code"] and file_data["trd_content"]:
            st.markdown("### Technical Requirements Document")
            st.success("TRD generated successfully!")

            with st.expander("View Generated TRD Content", expanded=True):
                st.markdown(file_data["trd_content"])

            st.markdown("#### System Architecture Diagram")
            st_mermaid(file_data["mermaid_code"], key=f"mermaid_{file_name}")

            doc_stream = create_trd_word_document(file_data["trd_content"], file_data["mermaid_code"])
            if doc_stream:
                st.download_button(
                    label="Download Full TRD (Word Document)",
                    data=doc_stream,
                    file_name=f"TRD_{file_name}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key=f"download_{file_name}"
                )

            with st.expander("View and Copy Mermaid.js Code"):
                st.code(file_data["mermaid_code"], language="mermaid")
        
        st.divider()

# Display total token count
st.sidebar.markdown("---")
