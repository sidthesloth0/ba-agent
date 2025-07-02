# prompts.py

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
As a senior business analyst, create a comprehensive Technical Requirements Document (TRD) in Markdown format based on the provided business plan.

**TRD Structure:**
Follow this structure precisely. ONLY include sections if the business plan provides relevant information.

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
(Create a plain text table with these columns: | FR-ID | Requirement | Description |)

# 4. UI Screen Specifications
(ONLY include this section if UI/UX details are mentioned. Use '## Screen: [Screen Name]' as a sub-header for each screen.)

# 5. User Roles and Permissions
(ONLY include this section if user roles are described. Create a plain text table: | Role | Permissions |)

# 6. Technical Specifications
(ONLY include this section if technical details are provided.)
## Database Schema
(Propose a high-level database schema if applicable)
## API Endpoints
(Suggest key API endpoints if applicable)

# 7. Non-Functional Requirements
(ONLY include this section if NFRs like performance, security, or scalability are mentioned.)
## Performance
(Describe performance expectations)
## Security
(Outline security considerations)
## Scalability
(Mention scalability requirements)

**Business Plan Content:**
{md_text}
"""