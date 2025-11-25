"""Google Slides API integration."""

import re


def extract_presentation_id(url_or_id: str) -> str:
    """Extract presentation ID from URL or validate bare ID.

    Args:
        url_or_id: Google Slides URL or bare presentation ID

    Returns:
        The presentation ID

    Raises:
        ValueError: If input doesn't contain a valid presentation ID
    """
    if not url_or_id:
        raise ValueError("Empty input")

    # Pattern matches IDs that are 20+ chars of alphanumeric, dash, underscore
    pattern = r"([a-zA-Z0-9_-]{20,})"
    match = re.search(pattern, url_or_id)

    if not match:
        raise ValueError(f"Invalid presentation URL or ID: {url_or_id}")

    return match.group(1)
