# prompts.py

GEMINI_MODEL = "gemini-2.0-flash"

SUMMARIZE_PROMPT = """
Please provide a concise summary of the following business plan text.
Focus on the key points, objectives, and strategies.
The summary should be a few paragraphs long.

Business Plan Text:
{md_text}
"""

ANALYZE_PROMPT = """
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

MERMAID_PROMPT = """
As a technical architect, create a Mermaid.js diagram from the business plan.
- Diagram must be top-down (`graph TD`).
- Outline system architecture, components, and user flow.
- Output ONLY raw Mermaid.js code using standard Mermaid syntax like `id[Description]`.
- CRITICAL: The text inside the node brackets (e.g., "Description") MUST NOT contain any parentheses or brackets. For example, instead of `A[Node with (parentheses)]`, write `A[Node with parentheses]`.
- No explanations, markdown fences, custom styles, or link labels.

Business Plan:
{md_text}
"""

TRD_PROMPT = """
As a senior business analyst, create a comprehensive Technical Requirements Document (TRD) in Markdown format based on the provided business plan. The entire output must be a single, valid Markdown document. **Do not wrap the output in markdown code fences (```).**

**TRD Structure:**
Follow this structure precisely.

# 1. Introduction
## Project Overview
(A brief summary of the project's purpose and scope)
## Objectives
(List the key goals of the project)

# 2. System Overview
## High-Level Architecture
(Describe the proposed architecture)
## System Components
(Detail the main components or modules)

# 3. Functional Requirements
(Create a Markdown table with these columns: | FR-ID | Requirement | Description |)

# 4. UI Screen Specifications
(Analyze any provided images for UI/UX details. If no specific UI details are mentioned or visible, state "No UI/UX details were specified in the business plan.")

# 5. User Roles and Permissions
(Describe user roles if mentioned. If not, state "No specific user roles were defined." Create a Markdown table if roles are present: | Role | Permissions |)

# 6. Technical Specifications
(Detail technical specifications if provided. If not, state "No technical specifications were detailed.")
## Database Schema
(Propose a high-level database schema if applicable. If not, state "Not applicable.")
## API Endpoints
(Suggest key API endpoints if applicable. If not, state "Not applicable.")

# 7. Non-Functional Requirements
(Describe NFRs like performance, security, or scalability. If none are mentioned, state "No non-functional requirements were specified.")
## Performance
(Describe performance expectations)
## Security
(Outline security considerations)
## Scalability
(Mention scalability requirements)

**Business Plan Content:**
{md_text}
"""

EPICS_USER_STORIES_PROMPT = """
As an Agile Product Owner, create a list of epics and user stories in Markdown format based on the provided business plan.

**Output Structure:**
Follow this structure precisely. For each epic, create a Markdown table with user stories.

## Epic: [Epic Name]
**Description:** [Briefly describe the epic's goal.]

| User Story | Description | Acceptance Criteria |
| --- | --- | --- |
| [Story Title] | As a [user type], I want [goal] so that [benefit]. | - Given [context], when [action], then [outcome]. - [Criterion 2] |
| [Story Title 2] | As a [user type], I want [goal] so that [benefit]. | - [Criterion 1] | - [Criterion 2] |

**Business Plan Content:**
{md_text}
"""