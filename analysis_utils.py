# analysis_utils.py
from typing import Tuple

def count_epics_and_stories(markdown_text: str) -> Tuple[int, int]:
    """
    Parses a markdown string to count the number of epics and user stories.

    Args:
        markdown_text: The markdown string containing epics and user stories.

    Returns:
        A tuple containing the epic count and the user story count.
    """
    if not markdown_text or not isinstance(markdown_text, str):
        return 0, 0

    epic_count = markdown_text.count("## Epic:")
    
    story_count = 0
    lines = markdown_text.splitlines()
    for line in lines:
        # A story row starts with '|' and is not a header or separator
        if line.strip().startswith('|') and "User Story" not in line and "---" not in line:
            # Ensure it's a valid table row with content, not just empty pipes
            parts = [part.strip() for part in line.strip().split('|') if part.strip()]
            if len(parts) >= 3:  # A valid story has at least 3 columns
                story_count += 1
                
    return epic_count, story_count
