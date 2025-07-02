import streamlit as st
import google.generativeai as genai
import re


def summarize_text(md_text):
    """Generates a concise summary of the text."""
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Please provide a concise summary of the following business plan text.
    Focus on the key points, objectives, and strategies.
    The summary should be a few paragraphs long.

    Business Plan Text:
    {md_text}
    """
    
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

