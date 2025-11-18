"""Landing Page Scraper Agent"""

from crewai import Agent
from tools.playwright_scraping_tool import scrape_landing_page
from tools.trafilatura_parser_tool import parse_with_trafilatura
from utils.llm_config import get_gemini_llm


def create_landing_page_scraper() -> Agent:
    """
    Creates the Landing Page Scraper agent

    This agent extracts structured text content from landing pages.
    """
    return Agent(
        role="Landing Page Scraper",
        goal="Extrahiere vollständigen und strukturierten Text-Content von Landingpages, inklusive dynamischer Inhalte",
        backstory="""Du bist spezialisiert auf robustes Web-Scraping und kennst alle
        Tricks moderner Webseiten. Du hast Erfahrung mit:

        - JavaScript-gerenderten Single Page Applications
        - Cookie-Bannern und Consent-Dialogen
        - Lazy-Loading und dynamischen Inhalten
        - Verschiedenen CMS-Systemen und Frameworks

        Du verwendest Playwright für komplexe Seiten und fällst auf trafilatura
        zurück für statische Seiten. Du extrahierst sauber strukturierte Texte
        ohne Boilerplate und Noise.

        Bei Problemen gibst du klare Fehlermeldungen, damit andere Agents
        entsprechend reagieren können.""",
        tools=[scrape_landing_page, parse_with_trafilatura],
        llm=get_gemini_llm(),
        verbose=True,
        allow_delegation=False,
    )
