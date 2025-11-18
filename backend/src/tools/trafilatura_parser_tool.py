"""Trafilatura Parser Tool - Fast Path for Static Pages"""

from crewai_tools import tool
from typing import Any
import trafilatura
import requests


@tool("Trafilatura Fast Parser")
def parse_with_trafilatura(url: str) -> dict:
    """Fast text extraction for static HTML pages.
    Use this as a fallback when Playwright is too slow or fails.

    Args:
        url: URL to parse

    Returns:
        dict with extracted content including success status, url, text, and text_length
    """
    try:
        # Download page
        downloaded = trafilatura.fetch_url(url)

        if not downloaded:
            return {
                "success": False,
                "url": url,
                "error": "Failed to download page",
            }

        # Extract text
        text = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=True,
            no_fallback=False,
        )

        if not text:
            return {
                "success": False,
                "url": url,
                "error": "Failed to extract text content",
            }

        return {
            "success": True,
            "url": url,
            "text": text,
            "text_length": len(text),
        }

    except Exception as e:
        return {
            "success": False,
            "url": url,
            "error": f"Parsing failed: {str(e)}",
        }
