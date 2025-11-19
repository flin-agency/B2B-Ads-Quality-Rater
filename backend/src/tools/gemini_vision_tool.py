"""Gemini Vision Tool for Ad Image Analysis"""

from crewai.tools import tool
from typing import Optional, Any
import google.generativeai as genai
from google.generativeai import types
import requests
import os
import base64
import re
import time


# Initialize Gemini client
def get_gemini_client():
    """Get or create Gemini client"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    model_name = os.getenv("MODEL", "gemini-2.5-flash")
    genai.configure(api_key=api_key)
    client = genai.GenerativeModel(model_name)
    return client, model_name


@tool("Gemini Vision Analyzer")
def analyze_ad_image(image_url: str) -> dict:
    """Analyzes advertisement images using Gemini 2.5 Flash Vision.

    Args:
        image_url: The URL or local file path to the ad image (required)

    Returns:
        JSON with 'success' (bool), 'analysis' (string), and 'image_source' (string)
        The analysis includes: colors, composition quality, emotional tone, CTA visibility, and brand elements.

    Example:
        analyze_ad_image("/tmp/tmpX1Y2Z3.jpg")
    """
    prompt = None  # Always use default prompt
    try:
        # Get Gemini client
        client, model_name = get_gemini_client()

        # Use default prompt if none provided
        if not prompt:
            prompt = """Analyze this advertisement image clearly and concisely:

1. Format: 1:1 or other? (important for LinkedIn)
2. Colors: Dominant hex codes
3. Composition Score: 0-100
4. Authenticity: Stock photo or authentic?
5. Text Overlay: How many words?
6. CTA Visibility: 0-100
7. Brand Elements: Yes/No

IMPORTANT: Detect the language from any text in the image, and respond in that SAME LANGUAGE.
If the ad has English text, respond in English. If German text, respond in German, etc.
MAX 6 sentences. Be clear and constructive."""

        # Validate input
        if not image_url:
            return {
                "success": False,
                "error": "image_url must be provided",
            }

        display_source = image_url if not image_url.startswith("data:image") else "[Base64 Data URL]"

        if image_url.startswith("data:image"):
            # Base64 data URL (from screenshot upload)
            match = re.match(r'data:(image/\w+);base64,(.+)', image_url)
            if match:
                final_mime_type = match.group(1)
                base64_data = match.group(2)
            else:
                final_mime_type = "image/jpeg"
                base64_data = re.sub('^data:image/.+;base64,', '', image_url)

            final_bytes = base64.b64decode(base64_data)

        elif image_url.startswith(("http://", "https://")):
            # Fetch from URL
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            final_bytes = response.content

            # Detect MIME type from URL
            final_mime_type = "image/jpeg"  # default
            if image_url.lower().endswith('.png'):
                final_mime_type = "image/png"
            elif image_url.lower().endswith('.gif'):
                final_mime_type = "image/gif"
            elif image_url.lower().endswith('.webp'):
                final_mime_type = "image/webp"

        else:
            # Local file
            with open(image_url, 'rb') as f:
                final_bytes = f.read()

            # Detect MIME type from file extension
            final_mime_type = "image/jpeg"  # default
            if image_url.lower().endswith('.png'):
                final_mime_type = "image/png"
            elif image_url.lower().endswith('.gif'):
                final_mime_type = "image/gif"
            elif image_url.lower().endswith('.webp'):
                final_mime_type = "image/webp"

        # Validate image size (max 10MB for Gemini)
        MAX_IMAGE_SIZE = 10 * 1024 * 1024
        if len(final_bytes) > MAX_IMAGE_SIZE:
            return {
                "success": False,
                "error": f"Image too large for analysis. Maximum size is 10MB, got {len(final_bytes) / (1024*1024):.1f}MB",
                "image_source": display_source,
            }

        # Create Part from bytes (proper Gemini SDK method)
        # For google-generativeai package, we pass a dict for inline data
        image_part = {
            "mime_type": final_mime_type,
            "data": final_bytes
        }

        # Generate analysis with retry logic (up to 3 attempts)
        max_retries = 3
        last_error = None

        for attempt in range(max_retries):
            try:
                response = client.generate_content(
                    contents=[prompt, image_part],
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.1,
                        max_output_tokens=4096,
                    )
                )

                # Debug: Log response structure
                print(f"[DEBUG] Gemini response received (attempt {attempt + 1})")
                print(f"[DEBUG] Has candidates: {hasattr(response, 'candidates')}")

                # Check if response has text
                if not hasattr(response, 'text') or not response.text or response.text.strip() == "":
                    # Check for safety ratings or blocked content
                    if hasattr(response, 'candidates') and response.candidates:
                        candidate = response.candidates[0]
                        print(f"[DEBUG] Candidate finish_reason: {getattr(candidate, 'finish_reason', 'None')}")
                        print(f"[DEBUG] Candidate safety_ratings: {getattr(candidate, 'safety_ratings', 'None')}")

                        if hasattr(candidate, 'finish_reason'):
                            finish_reason = str(candidate.finish_reason)
                            return {
                                "success": False,
                                "error": f"Gemini could not analyze the image (reason: {finish_reason}). The image may have been blocked by safety filters. Please try a different image.",
                                "image_source": display_source,
                            }

                    print(f"[DEBUG] Empty response, no finish_reason found")
                    return {
                        "success": False,
                        "error": "Gemini could not create an analysis. The image might be too small, unclear, or blocked by filters. Please try a different image.",
                        "image_source": display_source,
                    }

                print(f"[DEBUG] Success! Analysis length: {len(response.text)} chars")
                return {
                    "success": True,
                    "analysis": response.text,
                    "image_source": display_source,
                }

            except Exception as e:
                last_error = e
                print(f"[DEBUG] Attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    # Exponential backoff: 1s, 2s
                    wait_time = 2 ** attempt
                    print(f"[DEBUG] Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    # All retries failed
                    print(f"[DEBUG] All retries failed. Last error: {str(e)}")
                    raise

    except requests.exceptions.RequestException as e:
        error_source = "[Image]"
        if image_url and not image_url.startswith("data:image"):
            error_source = image_url

        return {
            "success": False,
            "error": f"Failed to fetch image: {str(e)}",
            "image_source": error_source,
        }
    except Exception as e:
        error_source = "[Image]"
        if image_url and not image_url.startswith("data:image"):
            error_source = image_url

        return {
            "success": False,
            "error": f"Analysis failed: {str(e)}",
            "image_source": error_source,
        }
