"""Playwright Scraping Tool for Landing Page Content Extraction"""

from crewai_tools import tool
from typing import Any
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import trafilatura


@tool("Playwright Landing Page Scraper")
def scrape_landing_page(url: str, timeout: int = 20000) -> dict:
    """Scrapes full text content from landing pages.
    Supports JavaScript-rendered pages, handles cookie banners, lazy loading.

    Args:
        url: URL of the landing page to scrape
        timeout: Timeout in milliseconds (default: 20000)

    Returns:
        dict with scraped content including success status, url, text, and text_length
    """
    try:
        with sync_playwright() as p:
            # Launch with faster settings
            browser = p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )
            context = browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = context.new_page()

            try:
                # Navigate to page - use domcontentloaded (faster than networkidle)
                page.goto(url, wait_until="domcontentloaded", timeout=timeout)

                # Quick cookie banner handling (try first match only, don't iterate all)
                try:
                    page.click(
                        'button:has-text("Accept"), button:has-text("Akzeptieren"), #onetrust-accept-btn-handler',
                        timeout=1000  # Only wait 1 second
                    )
                except:
                    pass  # No cookie banner or already accepted

                # Scroll to bottom (trigger lazy loading) with shorter wait
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(500)  # Reduced from 2s to 0.5s

                # Get HTML
                html = page.content()

                # Extract text with trafilatura
                text = trafilatura.extract(
                    html,
                    include_comments=False,
                    include_tables=True,
                    no_fallback=False,
                )

                if not text:
                    # Fallback: get all text
                    text = page.inner_text("body")

                return {
                    "success": True,
                    "url": url,
                    "text": text,
                    "text_length": len(text) if text else 0,
                }

            except PlaywrightTimeout:
                return {
                    "success": False,
                    "url": url,
                    "error": f"Page load timeout ({timeout}ms)",
                }
            except Exception as e:
                return {
                    "success": False,
                    "url": url,
                    "error": f"Scraping failed: {str(e)}",
                }
            finally:
                context.close()
                browser.close()

    except Exception as e:
        return {
            "success": False,
            "url": url,
            "error": f"Browser launch failed: {str(e)}",
        }
