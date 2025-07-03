import streamlit as st
import google.generativeai as genai
from prompts import SUMMARIZE_PROMPT, ANALYZE_PROMPT, MERMAID_PROMPT, TRD_PROMPT


def _generate_content_with_gemini(prompt, text_content, image_list=None):
    """
    Generic function to generate content using the Gemini model.

    Args:
        prompt (str): The prompt to use for generation.
        text_content (str): The text content to use.
        image_list (list, optional): A list of PIL Image objects. Defaults to None.

    Returns:
        tuple: A tuple containing the generated content (str) and a dictionary
               with token usage information, or (None, None) if an error occurs.
    """
    if not text_content:
        return None, None

    model = genai.GenerativeModel(model_name="gemini-1.5-flash")

    prompt_parts = [prompt, text_content]
    if image_list:
        prompt_parts.extend(image_list)

    try:
        response = model.generate_content(prompt_parts)
        
        prompt_tokens = model.count_tokens(prompt_parts).total_tokens
        output_tokens = model.count_tokens(response.text).total_tokens
        
        token_info = {
            "prompt": prompt_tokens,
            "output": output_tokens,
            "total": prompt_tokens + output_tokens,
        }
        return response.text, token_info
    except Exception as e:
        st.error(f"An error occurred during content generation: {e}")
        return None, None


def summarize_text(text_content, image_list=None):
    """
    Generates a summary of the given text and images using the Gemini model.

    Args:
        text_content (str): The text content to summarize.
        image_list (list, optional): A list of PIL Image objects. Defaults to None.

    Returns:
        tuple: A tuple containing the generated summary (str) and a dictionary
               with token usage information, or (None, None) if an error occurs.
    """
    return _generate_content_with_gemini(SUMMARIZE_PROMPT, text_content, image_list)
    

def analyze_with_gemini(text_content, image_list=None):
    """
    Analyzes the given text and images using the Gemini model.

    Args:
        text_content (str): The text content to analyze.
        image_list (list, optional): A list of PIL Image objects. Defaults to None.

    Returns:
        tuple: A tuple containing the analysis result (str) and a dictionary
               with token usage information, or (None, None) if an error occurs.
    """
    return _generate_content_with_gemini(ANALYZE_PROMPT, text_content, image_list)


def generate_mermaid_req_doc(text_content, image_list=None):
    """
    Generates a Mermaid diagram documentation based on the given text and images.

    Args:
        text_content (str): The text content for the diagram.
        image_list (list, optional): A list of PIL Image objects. Defaults to None.

    Returns:
        tuple: A tuple containing the generated Mermaid code (str) and a dictionary
               with token usage information, or (None, None) if an error occurs.
    """
    response_text, token_info = _generate_content_with_gemini(MERMAID_PROMPT, text_content, image_list)
    if response_text:
        # Clean up the response to ensure it's valid Mermaid code
        cleaned_response = response_text.strip().replace("```mermaid", "").replace("```", "").strip()
        return cleaned_response, token_info
    return None, None


def generate_trd_content(text_content, image_list=None):
    """
    Generates TRD content based on the given text and images.

    Args:
        text_content (str): The text content for the TRD.
        image_list (list, optional): A list of PIL Image objects. Defaults to None.

    Returns:
        tuple: A tuple containing the generated TRD content (str) and a dictionary
               with token usage information, or (None, None) if an error occurs.
    """
    return _generate_content_with_gemini(TRD_PROMPT, text_content, image_list)

