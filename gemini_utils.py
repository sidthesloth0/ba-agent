import streamlit as st
import google.generativeai as genai
from prompts import SUMMARIZE_PROMPT, ANALYZE_PROMPT


def summarize_text(md_text):
    """Generates a concise summary of the text."""
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = SUMMARIZE_PROMPT.format(md_text=md_text)

    try:
        response = model.generate_content(prompt)
        usage = response.usage_metadata
        token_info = {
            "prompt": usage.prompt_token_count,
            "output": usage.candidates_token_count,
            "total": usage.total_token_count
        }
        return response.text, token_info
    except Exception as e:
        st.error(f"An error occurred during summarization: {e}")
        return None, None
    

def analyze_with_gemini(md_text, images):
    """Analyzes the business plan text and images using Gemini."""
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = ANALYZE_PROMPT.format(md_text=md_text)

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

