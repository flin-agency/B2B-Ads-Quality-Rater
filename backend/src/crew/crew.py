"""Ad Quality Rater Crew - Main Orchestrator"""

from crewai import Crew, Task, Process
from typing import Optional
import uuid
from datetime import datetime
import time
import json
import re

from agents.ad_visual_analyst import create_ad_visual_analyst
from agents.landing_page_scraper import create_landing_page_scraper
from agents.copywriting_expert import create_copywriting_expert
from agents.brand_consistency_agent import create_brand_consistency_agent
from agents.quality_rating_synthesizer import create_quality_rating_synthesizer


class AdQualityRaterCrew:
    """
    Main Crew orchestrator for Ad Quality Analysis

    This crew coordinates 5 agents in a sequential process to analyze
    ads and landing pages for quality, consistency, and brand compliance.
    """

    def __init__(
        self,
        ad_url: str,
        landing_page_url: str,
        brand_guidelines: Optional[dict] = None,
        target_audience: Optional[str] = None,
        campaign_goal: Optional[str] = None,
    ):
        self.ad_url = ad_url
        self.landing_page_url = landing_page_url
        self.brand_guidelines = brand_guidelines or {}
        self.target_audience = target_audience or "Allgemeine Zielgruppe"
        self.campaign_goal = campaign_goal or "Allgemeine Kampagne"
        self.report_id = str(uuid.uuid4())
        self.start_time = None

        # Create agents
        self.ad_visual_analyst = create_ad_visual_analyst()
        self.landing_page_scraper = create_landing_page_scraper()
        self.copywriting_expert = create_copywriting_expert()
        self.brand_consistency_agent = create_brand_consistency_agent()
        self.quality_rating_synthesizer = create_quality_rating_synthesizer()

    def _create_tasks(self) -> list[Task]:
        """Create all tasks with proper context dependencies"""

        # Task 1: Analyze Ad Visuals
        analyze_ad_task = Task(
            description=f"""Analyze the ad visual using Gemini Vision Tool.

            **Tool:** {{"image_url": "{self.ad_url}"}}
            **Target Audience:** {self.target_audience}

            **Evaluate and provide constructive feedback:**
            1. Format: 1:1 (optimal) or other? Score: X/100
            2. Authenticity: Stock photo or authentic?
            3. Text Overlay: Max 7 words (best practice) or more?
            4. Thumb-Stopper: Would you stop scrolling? Yes/No
            5. CTA visibility? Score: X/100
            6. Colors: [Hex codes]

            **Improvement:** Specific recommendation OR "Good as is"

            IMPORTANT: Detect the language from any text in the ad image, and respond in that SAME LANGUAGE.
            If the ad has English text, respond in English. If German, respond in German, etc.
            Be clear and constructive. MAX 6 sentences.""",
            expected_output="""Clear, constructive visual analysis (max 6 sentences) with score and specific improvement suggestions. Response in the SAME LANGUAGE as the ad content.""",
            agent=self.ad_visual_analyst,
        )

        # Task 2: Scrape Landing Page
        scrape_lp_task = Task(
            description=f"""Extrahiere den vollständigen Text-Content von folgender Landingpage: {self.landing_page_url}

            Verwende Playwright für dynamische Seiten und trafilatura als Fallback.

            Achte auf:
            - Vollständige Extraktion aller sichtbaren Texte
            - Headlines, Subheadlines, Body-Text
            - Call-to-Actions
            - Entfernung von Boilerplate (Footer, Cookie-Banner-Text, etc.)

            Bei Problemen (Timeout, 404, etc.) gib eine klare Fehlermeldung zurück.""",
            expected_output="""Extrahierter Text-Content der Landingpage als String,
            oder Fehlermeldung bei Problemen.""",
            agent=self.landing_page_scraper,
        )

        # Task 3: Copywriting Analysis
        copywriting_task = Task(
            description=f"""Evaluate copy quality. Be honest and constructive.

            **Input:**
            - Ad Analysis: {{analyze_ad_task.output}}
            - Landing Page: {{scrape_lp_task.output}}

            **Evaluate:**
            1. Consistency Ad→LP: X/100
            2. Tone: Educational or salesy?
            3. CTA: Appropriate? Yes/No
            4. Pain Point: Clear? Yes/No
            5. PIO Formula: Present? Yes/No
            6. Length: Intro >150 chars? Headline >70 chars?
            7. Triggers: Which? (Specificity, Familiarity, etc.)

            **Improvement:** Ready-to-use text suggestion OR "Good as is"

            IMPORTANT: Use the SAME LANGUAGE as detected in the ad visual analysis.
            Be clear and constructive. MAX 6 sentences.""",
            expected_output="""Clear copywriting analysis (max 6 sentences) with score and ready-to-use improvement text. Response in the SAME LANGUAGE as the ad content.""",
            agent=self.copywriting_expert,
            context=[analyze_ad_task, scrape_lp_task],
        )

        # Task 4: Brand Compliance Check (OPTIONAL - only if guidelines provided)
        brand_compliance_task = Task(
            description=f"""ONLY if brand guidelines are provided: Quick brand compliance check.

            **Brand Guidelines:**
            {self.brand_guidelines if self.brand_guidelines else "NO Guidelines - SKIP this analysis"}

            **If guidelines provided:**
            - Quick check: Tone, colors, forbidden words
            - Score (0-100): Overall rating
            - MAX 2-3 sentences feedback

            **If NO guidelines:**
            - Write: "No brand guidelines provided."

            IMPORTANT: Use the SAME LANGUAGE as detected in previous analyses.
            Be BRIEF. Maximum 3 sentences.""",
            expected_output="""Brief brand analysis (max 3 sentences) OR "No guidelines provided". Response in the SAME LANGUAGE as the ad content.""",
            agent=self.brand_consistency_agent,
            context=[analyze_ad_task, scrape_lp_task],
        )

        # Task 5: Synthesize Final Report
        synthesize_report_task = Task(
            description=f"""Create a CONCISE, CLEAR performance report.

            **Input Analyses:**
            - Visual: {{analyze_ad_task.output}}
            - Copy: {{copywriting_task.output}}
            - Brand: {{brand_compliance_task.output}}

            **Report Structure (BRIEF!):**

            # 📊 Ad Performance Analysis

            **Score:** X/100 (Visual 40%, Copy 50%, Brand 10%)
            **Assessment:** [Good/Needs Improvement/Poor - BE HONEST]

            ---

            ## 🎨 Visual (MAX 4 sentences)
            - Format: [1:1 or other? Assessment]
            - Authenticity: [Stock photo? Yes/No]
            - Text Overlay: [Assessment]
            - **Improvement:** [Specific suggestion OR "Good as is"]

            ## ✍️ Copy (MAX 4 sentences)
            - Consistency Ad→LP: [Score 0-100]
            - Tone: [Salesy/Educational]
            - PIO Formula: [Yes/No]
            - **Improvement:** [Specific text suggestion OR "Good as is"]

            ## 🎯 Brand (MAX 2 sentences - OR skip if no guidelines)
            - [Brief feedback OR "No guidelines provided"]

            ## 🔥 TOP 2 IMPROVEMENTS (Only if needed!)

            **1. [Highest Impact - e.g. "Headline"]**
            ❌ Current: "[Show current text]"
            ✅ Suggested: "[Ready-to-use new text]"
            Expected Impact: +X%

            **2. [Second Priority - e.g. "CTA"]**
            ❌ Current: "[Show current text]"
            ✅ Suggested: "[Ready-to-use new text]"
            Expected Impact: +X%

            **RULES:**
            - BRIEF: Maximum 3-4 sentences per section
            - CLEAR: Be specific and constructive
            - ACTIONABLE: Every critique includes a concrete fix
            - FOCUS: Only TOP 2 improvements for highest impact
            - Skip brand section if no guidelines provided
            - LANGUAGE: Use the SAME LANGUAGE as detected in all previous analyses

            Be concise and constructive.""",
            expected_output="""Concise performance report (max 15 sentences total) with:
            - Clear assessment
            - Top 2 improvements with ready-to-use text
            - Constructive feedback
            - Response in the SAME LANGUAGE as the ad content""",
            agent=self.quality_rating_synthesizer,
            context=[analyze_ad_task, scrape_lp_task, copywriting_task, brand_compliance_task],
        )

        return [
            analyze_ad_task,
            scrape_lp_task,
            copywriting_task,
            brand_compliance_task,
            synthesize_report_task,
        ]

    def kickoff(self) -> str:
        """
        Start the crew analysis

        Returns:
            Text report from the analysis
        """
        self.start_time = time.time()

        try:
            # Create crew
            crew = Crew(
                agents=[
                    self.ad_visual_analyst,
                    self.landing_page_scraper,
                    self.copywriting_expert,
                    self.brand_consistency_agent,
                    self.quality_rating_synthesizer,
                ],
                tasks=self._create_tasks(),
                process=Process.sequential,
                verbose=True,
            )

            # Execute crew
            result = crew.kickoff()

            # Return the text result directly
            processing_time = time.time() - self.start_time

            # Convert result to string
            result_text = str(result)

            # Add processing time footer
            result_text += f"\n\n---\n\n**⏱️ Verarbeitungszeit:** {processing_time:.1f} Sekunden"

            return result_text

        except Exception as e:
            processing_time = time.time() - self.start_time if self.start_time else 0

            return f"""# ❌ Analyse Fehlgeschlagen

**Fehler:** {str(e)}

**Verarbeitungszeit:** {processing_time:.1f} Sekunden

Bitte versuchen Sie es erneut oder kontaktieren Sie den Support."""
