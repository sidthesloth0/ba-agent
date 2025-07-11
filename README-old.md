[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ba-agent.streamlit.app/)
# Business Analysis Agent
## About:
This application allows you to:
 - upload one or more PDF business plans
 - extracts the text and images for each file
 - uses Google Gemini to provide business analysis on a per-file or global basis
 - generate a technical requirements document (TRD) for each file or all files combined
 - create a technical requirements diagram using Mermaid.js
 - preview TRD in Markdown on the site
 - export the TRD including the Mermaid.js diagram, in a Word Document

# Features
 - Multi-File PDF Text and Image extraction
 - Per-File and Global (All-Files-Combined) Analysis
 - Batch actions to process all files at once
 - On-demand Text Summarization for Token Optimization
 - LLM-Powered Business Plan Analysis
 - Comprehensive Technical Requirements Document (TRD) Generation
 - Generation of Epics and User Stories for developers
 - System Architecture Diagram Generation (Mermaid.js)
 - Downloadable Word Document Output for TRD (including diagrams, epics, and user stories)
 - Configurable AI Model via a single variable
 - Interactive Table of Contents
 - Real-time Token Usage Tracking

## How to use this app?
Here are instructions on how to get the project running locally.
- **Prerequisites**:
    - Python 3.13.5
    - All required packages are listed in `requirements.txt`.
- **Installation**
    - clone the repository
    - Enter relevant command below to create the virtual environment `(.venv)`:
        - For Windows: `.venv\Scripts\activate`
        - For Mac/Linux: `source .venv/bin/activate`
    - `pip install -r requirements`
    - make a `.env` file in the root directory if it is not already made
    - Enter exactly `GOOGLE_API_KEY=` and then your Google API key in the `.env` file
- **How to run the app**
    - Make sure you are in the `(.venv)` virtual environment.
    - If you are not, enter this command in the command line:
      - For Windows: `.venv\Scripts\activate`
      - For Mac/Linux: `source .venv/bin/activate`
    - Enter this to run the app:
    `streamlit run ba-agent.py`
## How to use the app
1. **Upload one or more PDF files using the given interface**
    - You can upload a single file or multiple files for batch analysis.
2. **View the extracted content**
    - For each uploaded file, the app will display the full text and any extracted images in its own section.
3. **Navigate Between Files**
    - Use the "Processed Files" list in the sidebar to quickly jump to the analysis section for a specific document.
4. **Generate Summaries, Analyses, and TRDs**
    - **Per-File Actions**: Within each file's section, you can generate a summary, run a business analysis, or create a TRD for that specific file.
    - **Batch Actions (for multiple files)**: At the top of the page, use the "Generate All Summaries", "Analyze All Business Plans", or "Generate All TRDs" buttons to run the respective action on all uploaded files at once.
    - **Global Batch Actions (for multiple files)**: You can also treat all uploaded documents as a single, combined business plan. Use the buttons in the "Global Batch Actions" section to generate a unified summary, analysis, and TRD for all content.
5. **Use Summaries for Efficiency (Optional)**
    - After generating a summary (either per-file or global), a checkbox will appear. You can use the summary for subsequent analysis and TRD generation to reduce token usage and costs.
6. **Download TRDs**
    - After a TRD is generated (either per-file or global), you can download it as a `.docx` file, which includes the structured text, the system architecture diagram, and a list of epics and user stories for developers.
7. **Monitor Token Usage**
    - Keep an eye on the token counter in the sidebar to track API usage throughout your session.
8. **Customize AI Model and Prompts**
    - You can change the Gemini model used for analysis by editing the `GEMINI_MODEL` variable in the `prompts.py` file. You can also customize the instructions given to the LLM by editing the prompt variables in the same file. This allows you to tailor the model, summarization, analysis, TRD, and diagram generation prompts to your specific needs.


## Code Structure

- `ba-agent.py`: Main Streamlit app, UI, and state management logic
- `gemini_utils.py`: All Gemini/LLM-related functions (summarization, analysis, etc.)
- `docx_utils.py`: Word document and Mermaid.js diagram generation
- `prompts.py`: Contains the configuration for the `GEMINI_MODEL` and all user-editable AI prompts for summarization, analysis, TRD, diagrams, and epics/user stories.


## Troubleshooting

- **GOOGLE_API_KEY not found**: Make sure your `.env` file is present in the root directory and contains your API key in the format `GOOGLE_API_KEY=your_key_here`.
- **File Locking Issues on Windows**: If you encounter errors related to file access, ensure no other processes are using the temporary PDF files. The app is designed to clean up these files automatically.
- **ImportError**: Ensure all required files (`prompts.py`, `gemini_utils.py`, `docx_utils.py`) are in the same directory as `ba-agent.py`.
- **Package errors**: Run `pip install -r requirements.txt` in your virtual environment to install all dependencies.