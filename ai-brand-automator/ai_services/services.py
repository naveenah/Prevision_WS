"""
AI Services for BrandForge AI
Integration with Google Gemini AI
"""

import os
import time
import logging
from typing import Dict, List, Any, Optional
from django.conf import settings
import google.generativeai as genai
from .models import AIGeneration
from brand_automator.validators import sanitize_ai_prompt

logger = logging.getLogger(__name__)


class GeminiAIService:
    """
    Service for interacting with Google Gemini AI
    """

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY") or settings.GOOGLE_API_KEY
        self.model_name = "gemini-1.5-flash"
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.model_name)
                logger.info(
                    f"Gemini AI service initialized with model: " f"{self.model_name}"
                )
            except Exception as e:
                logger.error(f"Failed to initialize Gemini AI: {str(e)}")
                self.model = None
        else:
            logger.warning(
                "GOOGLE_API_KEY not configured. AI service will use "
                "fallback responses."
            )
            self.model = None

    def generate_brand_strategy(self, company_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate brand strategy content using AI
        """
        prompt = self._build_brand_strategy_prompt(company_data)

        start_time = time.time()

        try:
            if self.model:
                response = self.model.generate_content(prompt)
                ai_response = response.text

                # Parse the AI response (assuming it returns structured text)
                # For simplicity, we'll extract key sections
                vision = self._extract_section(ai_response, "Vision Statement")
                mission = self._extract_section(ai_response, "Mission Statement")
                values = self._extract_list_section(ai_response, "Core Values")
                positioning = self._extract_section(
                    ai_response, "Positioning Statement"
                )

                result = {
                    "vision_statement": vision
                    or (
                        f"Our vision is to revolutionize the "
                        f"{company_data.get('industry', 'industry')} "
                        f"through innovative solutions."
                    ),
                    "mission_statement": mission
                    or (
                        f"To provide exceptional "
                        f"{company_data.get('industry', 'services')} that solve "
                        f"{company_data.get('core_problem', 'key challenges')} "
                        f"for our customers."
                    ),
                    "values": values
                    or [
                        "Innovation",
                        "Customer Focus",
                        "Excellence",
                        "Integrity",
                    ],
                    "positioning_statement": positioning
                    or (
                        f"The leading {company_data.get('industry', 'solution')} "
                        f"for businesses seeking to overcome "
                        f"{company_data.get('core_problem', 'challenges')}."
                    ),
                }
            else:
                # Fallback to mock response if API not configured
                result = {
                    "vision_statement": (
                        f"Our vision is to revolutionize the "
                        f"{company_data.get('industry', 'industry')} through "
                        f"innovative solutions that empower businesses."
                    ),
                    "mission_statement": (
                        f"To provide exceptional "
                        f"{company_data.get('industry', 'services')} that solve "
                        f"{company_data.get('core_problem', 'key challenges')} "
                        f"for our customers."
                    ),
                    "values": [
                        "Innovation",
                        "Customer Focus",
                        "Excellence",
                        "Integrity",
                        "Collaboration",
                    ],
                    "positioning_statement": (
                        f"The leading {company_data.get('industry', 'solution')} "
                        f"for businesses seeking to overcome "
                        f"{company_data.get('core_problem', 'challenges')}."
                    ),
                }

        except Exception as e:
            # Log error and use fallback
            logger.error(
                f"AI brand strategy generation failed: {str(e)}", exc_info=True
            )
            result = {
                "vision_statement": (
                    f"Our vision is to revolutionize the "
                    f"{company_data.get('industry', 'industry')} through "
                    f"innovative solutions."
                ),
                "mission_statement": (
                    f"To provide exceptional "
                    f"{company_data.get('industry', 'services')} that solve "
                    f"{company_data.get('core_problem', 'key challenges')} "
                    f"for our customers."
                ),
                "values": [
                    "Innovation",
                    "Customer Focus",
                    "Excellence",
                    "Integrity",
                ],
                "positioning_statement": (
                    f"The leading {company_data.get('industry', 'solution')} "
                    f"for businesses seeking to overcome "
                    f"{company_data.get('core_problem', 'challenges')}."
                ),
            }

        processing_time = time.time() - start_time

        # Log the generation
        try:
            AIGeneration.objects.create(
                tenant=company_data.get("tenant"),
                content_type="brand_strategy",
                prompt=prompt,
                response=str(result),
                tokens_used=len(prompt.split())
                + len(str(result).split()),  # Rough estimate
                processing_time=processing_time,
            )
        except Exception as e:
            logger.error(f"Failed to log AI generation: {str(e)}", exc_info=True)

        return result

    def generate_brand_identity(self, company_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate brand identity elements using AI
        """
        prompt = self._build_brand_identity_prompt(company_data)

        start_time = time.time()

        try:
            if self.model:
                response = self.model.generate_content(prompt)
                ai_response = response.text

                # Parse the AI response
                color_palette = self._extract_section(ai_response, "Color Palette")
                fonts = self._extract_section(
                    ai_response, "Typography"
                ) or self._extract_section(ai_response, "Fonts")
                messaging = self._extract_section(
                    ai_response, "Messaging Guide"
                ) or self._extract_section(ai_response, "Tone")

                result = {
                    "color_palette_desc": color_palette
                    or (
                        "Primary: Deep Blue (#1a365d) for trust and "
                        "professionalism, Secondary: Teal (#319795) for "
                        "innovation, Accent: Orange (#ed8936) for energy"
                    ),
                    "font_recommendations": fonts
                    or (
                        "Primary: Inter (clean, modern sans-serif for body "
                        "text), Secondary: Playfair Display (elegant serif "
                        "for headings)"
                    ),
                    "messaging_guide": messaging
                    or (
                        f"Professional yet approachable tone. Emphasize "
                        f"{company_data.get('brand_voice', 'innovation')} and "
                        f"customer success. Use clear, jargon-free language."
                    ),
                }
            else:
                # Fallback to mock response if API not configured
                result = {
                    "color_palette_desc": (
                        "Primary: Deep Blue (#1a365d) for trust and "
                        "professionalism, Secondary: Teal (#319795) for "
                        "innovation, Accent: Orange (#ed8936) for energy"
                    ),
                    "font_recommendations": (
                        "Primary: Inter (clean, modern sans-serif for body "
                        "text), Secondary: Playfair Display (elegant serif "
                        "for headings)"
                    ),
                    "messaging_guide": (
                        f"Professional yet approachable tone. Emphasize "
                        f"{company_data.get('brand_voice', 'innovation')} and "
                        f"customer success. Use clear, jargon-free language."
                    ),
                }

        except Exception as e:
            # Log error and use fallback
            logger.error(
                f"AI brand identity generation failed: {str(e)}", exc_info=True
            )
            result = {
                "color_palette_desc": (
                    "Primary: Deep Blue (#1a365d) for trust and "
                    "professionalism, Secondary: Teal (#319795) for "
                    "innovation, Accent: Orange (#ed8936) for energy"
                ),
                "font_recommendations": (
                    "Primary: Inter (clean, modern sans-serif for body "
                    "text), Secondary: Playfair Display (elegant serif "
                    "for headings)"
                ),
                "messaging_guide": (
                    f"Professional yet approachable tone. Emphasize "
                    f"{company_data.get('brand_voice', 'innovation')} and "
                    f"customer success. Use clear, jargon-free language."
                ),
            }

        processing_time = time.time() - start_time

        # Log the generation
        try:
            AIGeneration.objects.create(
                tenant=company_data.get("tenant"),
                content_type="brand_identity",
                prompt=prompt,
                response=str(result),
                tokens_used=len(prompt.split()) + len(str(result).split()),
                processing_time=processing_time,
            )
        except Exception as e:
            logger.error(f"Failed to log AI generation: {str(e)}", exc_info=True)

        return result

    def chat_with_brand_context(self, message: str, context: Dict[str, Any]) -> str:
        """
        Chat with AI using brand context
        """
        # Sanitize user message to prevent prompt injection
        sanitized_message = sanitize_ai_prompt(message)

        prompt = self._build_chat_prompt(sanitized_message, context)

        # TODO: Replace with actual Gemini API call
        start_time = time.time()

        # Simple mock responses based on message content
        if "vision" in message.lower():
            response = (
                "Your vision statement should be aspirational and "
                "forward-looking. Consider what impact you want to have "
                "on your industry in 5-10 years."
            )
        elif "mission" in message.lower():
            response = (
                "Your mission statement should explain how you serve "
                "your customers and solve their problems today."
            )
        elif "values" in message.lower():
            response = (
                "Core values should guide your company's behavior and "
                "decision-making. Choose 3-5 values that truly "
                "represent your brand."
            )
        elif "positioning" in message.lower():
            response = (
                "Positioning is about how you want customers to perceive your "
                "brand relative to competitors. Focus on your unique strengths."
            )
        else:
            response = (
                "I'm here to help you build a strong brand strategy. "
                "What specific aspect would you like to discuss?"
            )

        processing_time = time.time() - start_time

        # Log the generation
        try:
            AIGeneration.objects.create(
                tenant=context.get("tenant"),
                content_type="content",
                prompt=prompt,
                response=response,
                tokens_used=80,
                processing_time=processing_time,
            )
        except Exception as e:
            logger.error(f"Failed to log chat AI generation: {str(e)}", exc_info=True)

        return response

    def analyze_market(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform market analysis using AI
        """
        prompt = self._build_market_analysis_prompt(company_data)

        # TODO: Replace with actual Gemini API call
        start_time = time.time()

        mock_response = {
            "competitor_analysis": (
                f"Key competitors in {company_data.get('industry', 'your industry')} "
                f"include established players focusing on traditional solutions. "
                f"Your unique advantage lies in addressing "
                f"{company_data.get('core_problem', 'specific customer needs')}."
            ),
            "market_opportunities": (
                "Growing demand for digital solutions, underserved "
                "customer segments, emerging technology trends."
            ),
            "recommendations": (
                "Focus on customer education, build thought leadership "
                "content, leverage digital marketing channels."
            ),
        }

        processing_time = time.time() - start_time

        # Log the generation
        AIGeneration.objects.create(
            tenant=company_data.get("tenant"),
            content_type="analysis",
            prompt=prompt,
            response=str(mock_response),
            tokens_used=200,
            processing_time=processing_time,
        )

        return mock_response

    def _build_brand_strategy_prompt(self, company_data: Dict[str, Any]) -> str:
        """Build prompt for brand strategy generation"""
        return f"""
        Generate a comprehensive brand strategy for a company with the
        following details:

        Company Name: {company_data.get('name', 'N/A')}
        Industry: {company_data.get('industry', 'N/A')}
        Target Audience: {company_data.get('target_audience', 'N/A')}
        Core Problem Solved: {company_data.get('core_problem', 'N/A')}
        Brand Voice: {company_data.get('brand_voice', 'N/A')}

        Please provide:
        1. Vision Statement (aspirational, 1-2 sentences)
        2. Mission Statement (how you serve customers, 1-2 sentences)
        3. Core Values (5 key values with brief descriptions)
        4. Positioning Statement (how you differentiate from competitors)

        Make it professional, compelling, and tailored to the company details provided.
        """

    def _build_brand_identity_prompt(self, company_data: Dict[str, Any]) -> str:
        """Build prompt for brand identity generation"""
        return f"""
        Generate brand identity elements for a company with these characteristics:

        Company Name: {company_data.get('name', 'N/A')}
        Industry: {company_data.get('industry', 'N/A')}
        Brand Voice: {company_data.get('brand_voice', 'N/A')}
        Target Audience: {company_data.get('target_audience', 'N/A')}

        Please provide:
        1. Color Palette: 3-4 colors with hex codes and usage guidelines
        2. Typography: Primary and secondary font recommendations
        3. Messaging Guide: Tone, voice, and communication guidelines

        Ensure the recommendations align with the brand voice and appeal to
        the target audience.
        """

    def _build_chat_prompt(self, message: str, context: Dict[str, Any]) -> str:
        """Build prompt for chat interactions"""
        company_info = context.get("company", {})
        return f"""
        You are an AI brand strategist helping a company build their brand.

        Company Context:
        - Name: {company_info.get('name', 'N/A')}
        - Industry: {company_info.get('industry', 'N/A')}
        - Target Audience: {company_info.get('target_audience', 'N/A')}
        - Core Problem: {company_info.get('core_problem', 'N/A')}
        - Brand Voice: {company_info.get('brand_voice', 'N/A')}

        User Message: {message}

        Provide helpful, professional advice about brand strategy and building.
        """

    def _build_market_analysis_prompt(self, company_data: Dict[str, Any]) -> str:
        """Build prompt for market analysis"""
        return f"""
        Perform a market analysis for a company with these details:

        Company Name: {company_data.get('name', 'N/A')}
        Industry: {company_data.get('industry', 'N/A')}
        Target Audience: {company_data.get('target_audience', 'N/A')}
        Core Problem Solved: {company_data.get('core_problem', 'N/A')}

        Please provide:
        1. Competitor Analysis: Key competitors and market positioning
        2. Market Opportunities: Growth areas and trends
        3. Strategic Recommendations: Actionable advice for market success

        Be specific and actionable in your analysis.
        """

    def _extract_section(self, text: str, section_name: str) -> Optional[str]:
        """Extract a section from AI response text"""
        import re

        pattern = rf"{section_name}[:\s]*(.*?)(?=\n\n|\n[A-Z]|$)"
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else None

    def _extract_list_section(
        self, text: str, section_name: str
    ) -> Optional[List[str]]:
        """Extract a list section from AI response text"""
        import re

        pattern = rf"{section_name}[:\s]*(.*?)(?=\n\n|\n[A-Z]|$)"
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            content = match.group(1).strip()
            # Split by common list separators
            items = re.split(r"[,;]|\sand\s|\sor\s", content)
            return [item.strip().strip("-•*").strip() for item in items if item.strip()]
        return None


# Global service instance
ai_service = GeminiAIService()
