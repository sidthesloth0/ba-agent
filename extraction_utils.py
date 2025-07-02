import re
import streamlit as st


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