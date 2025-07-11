[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ba-agent.streamlit.app/)
# Business Analysis Agent

The Business Analysis Agent is a powerful web application built with Streamlit and powered by Google's Gemini AI. It automates the process of analyzing business plans from PDF documents, generating summaries, detailed analyses, and comprehensive Technical Requirements Documents (TRDs).

## ✨ Key Features

-   **PDF Processing**: Upload one or more PDF files for analysis. The agent extracts both text and images.
-   **AI-Powered Summarization**: Generate concise summaries of documents to optimize token usage for further analysis.
-   **In-Depth Business Analysis**: Leverage Google's Gemini model to perform a deep analysis of the business plan content.
-   **Technical Requirements Document (TRD) Generation**: Automatically create a full TRD that includes:
    -   Detailed requirements content.
    -   A system architecture diagram generated in Mermaid.js syntax.
    -   A list of Epics and User Stories derived from the business plan.
-   **Epics & Stories Overview**: Get a quick numerical count of the generated epics and user stories.
-   **Batch & Global Analysis**:
    -   Process multiple files at once with batch actions for summarization and analysis.
    -   Combine all uploaded documents for a single, unified "Global Analysis" and TRD generation.
-   **Word Document Export**: Download the generated TRD, including diagrams and user stories, as a `.docx` file for both individual and global analyses.
-   **Token Tracking**: Monitor your API token consumption in real-time via a sidebar counter.
-   **Interactive UI**: A user-friendly interface built with Streamlit, featuring expanders and clear action buttons for a smooth workflow.

## 🛠️ Technology Stack

-   **Backend**: Python
-   **AI Model**: Google Gemini Flash
-   **Web Framework**: Streamlit
-   **PDF Processing**: PyMuPDF
-   **Document Generation**: python-docx
-   **Diagrams**: streamlit-mermaid

## 🚀 Setup and Installation

Follow these steps to get the Business Analysis Agent running on your local machine.

### 1. Prerequisites

-   Python 3.13.5
-   A Google API Key with the Gemini API enabled.

### 2. Clone the Repository

```bash
git clone https://github.com/sidthesloth0/ba-agent.git
cd ba-agent
```

### 3. Create a Virtual Environment (Recommended)

```bash
# For Windows
python -m venv .venv
.venv\Scripts\activate

# For macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```
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

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Set Up Environment Variables

Create a file named `.env` in the root directory of the project and add your Google API key:

```
GOOGLE_API_KEY=YOUR_API_KEY_HERE
```

## ▶️ How to Run

Make sure you are in the virtual environment:
```bash
# For Windows
.venv\Scripts\activate

# For macOS/Linux
source .venv/bin/activate
```
Once the setup is complete, run the following command in your terminal:

```bash
streamlit run ba-agent.py
```

The application will open in a new tab in your web browser.

## 📖 How to Use

1.  **Upload Files**: Start by uploading one or more business plan PDF files using the file uploader.
2.  **Generate Summaries**: (Optional but recommended) Use the "Generate Summary" button for each file or the "Generate All Summaries" batch action to create concise versions for analysis.
3.  **Analyze**: Click "Analyze Business Plan" to let the AI perform a detailed analysis.
4.  **Generate TRD**: Click "Generate TRD" to create the full technical requirements document, including the system diagram and user stories.
5.  **Global Actions**: If you uploaded multiple files, use the "Global Analysis" section to get a combined perspective.
6.  **Download**: Use the "Download" buttons to save the generated TRDs as Word documents.