"""
LangChain AI Agent Functions for BrandForge AI
Integrates with Google Gemini Pro 3 for brand generation
"""

import os
import json
import time
from typing import Dict, List, Optional
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage

# Import prompt templates
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from templates.prompts import (
    FOUNDATION_PROMPT,
    POSITIONING_PROMPT,
    COMPETITOR_ANALYSIS_PROMPT,
    BRAND_IDENTITY_PROMPT,
    KPI_INSIGHTS_PROMPT,
    REFINEMENT_PROMPT,
    ONE_PAGER_PROMPT,
    format_competitors_list,
    format_values_list
)

# Load environment variables
load_dotenv()

# Initialize Gemini model
def get_llm(temperature: float = 0.7, streaming: bool = False) -> ChatGoogleGenerativeAI:
    """
    Initialize and return a Gemini LLM instance.
    
    Args:
        temperature: Controls randomness (0.0 = deterministic, 1.0 = creative)
        streaming: Enable streaming responses
        
    Returns:
        Configured ChatGoogleGenerativeAI instance
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY not found in environment variables. "
            "Please add it to your .env file. "
            "Get your key from: https://makersuite.google.com/app/apikey"
        )
    
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=temperature,
        max_output_tokens=2048,
        convert_system_message_to_human=True,  # Gemini-specific
        streaming=streaming
    )


def retry_on_error(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator to retry function calls on failure with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries (doubles each time)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        time.sleep(current_delay)
                        current_delay *= 2  # Exponential backoff
                    else:
                        raise last_exception
            
            raise last_exception
        return wrapper
    return decorator


@retry_on_error(max_retries=3)
def generate_brand_foundations(
    company_name: str,
    target_audience: str,
    core_problem: str,
    brand_voice: str
) -> Dict[str, any]:
    """
    Generate Vision, Mission, and Core Values using Gemini.
    
    Args:
        company_name: Name of the company
        target_audience: Description of target audience
        core_problem: Problem the company solves
        brand_voice: Desired brand voice/tone
        
    Returns:
        Dict with keys: vision, mission, values (list)
        
    Raises:
        ValueError: If required parameters are missing
        Exception: If API call fails after retries
    """
    # Validate inputs
    if not all([company_name, target_audience, core_problem, brand_voice]):
        raise ValueError("All parameters are required for foundation generation")
    
    # Initialize LLM
    llm = get_llm(temperature=0.7)
    
    # Format prompt
    prompt = FOUNDATION_PROMPT.format(
        company_name=company_name,
        target_audience=target_audience,
        core_problem=core_problem,
        brand_voice=brand_voice
    )
    
    # Make API call
    response = llm.invoke([HumanMessage(content=prompt)])
    
    # Parse JSON response
    try:
        # Clean response (remove markdown code blocks if present)
        content = response.content.strip()
        if content.startswith("```json"):
            content = content.split("```json")[1].split("```")[0].strip()
        elif content.startswith("```"):
            content = content.split("```")[1].split("```")[0].strip()
        
        result = json.loads(content)
        
        # Validate structure
        required_keys = ["vision", "mission", "values"]
        if not all(key in result for key in required_keys):
            raise ValueError(f"Response missing required keys: {required_keys}")
        
        return result
        
    except json.JSONDecodeError as e:
        # If JSON parsing fails, return structured error
        raise ValueError(f"Failed to parse AI response as JSON: {str(e)}\nResponse: {response.content}")


@retry_on_error(max_retries=3)
def generate_positioning_statement(
    company_name: str,
    target_audience: str,
    core_problem: str,
    brand_voice: str,
    values: List[str]
) -> str:
    """
    Generate a positioning statement using Gemini.
    
    Args:
        company_name: Name of the company
        target_audience: Description of target audience
        core_problem: Problem the company solves
        brand_voice: Brand voice/tone
        values: List of core values
        
    Returns:
        Positioning statement as string
    """
    llm = get_llm(temperature=0.7)
    
    prompt = POSITIONING_PROMPT.format(
        company_name=company_name,
        target_audience=target_audience,
        core_problem=core_problem,
        brand_voice=brand_voice,
        values=format_values_list(values)
    )
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content.strip()


@retry_on_error(max_retries=3)
def analyze_competitors(
    company_name: str,
    positioning_statement: str,
    values: List[str],
    target_audience: str,
    competitors: List[str]
) -> str:
    """
    Generate competitive gap analysis using Gemini.
    
    Args:
        company_name: Name of the company
        positioning_statement: Current positioning
        values: Core values
        target_audience: Target audience description
        competitors: List of competitor names
        
    Returns:
        Gap analysis as markdown string
    """
    llm = get_llm(temperature=0.7)
    
    prompt = COMPETITOR_ANALYSIS_PROMPT.format(
        company_name=company_name,
        positioning_statement=positioning_statement,
        values=format_values_list(values),
        target_audience=target_audience,
        competitors_list=format_competitors_list(competitors)
    )
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content.strip()


@retry_on_error(max_retries=3)
def generate_brand_identity(
    company_name: str,
    brand_voice: str,
    values: List[str],
    target_audience: str,
    positioning: str
) -> Dict[str, str]:
    """
    Generate brand identity (colors, fonts, messaging guide) using Gemini.
    
    Args:
        company_name: Name of the company
        brand_voice: Brand voice/tone
        values: Core values
        target_audience: Target audience description
        positioning: Positioning statement
        
    Returns:
        Dict with keys: color_palette_desc, font_recommendations, messaging_guide
    """
    llm = get_llm(temperature=0.7)
    
    prompt = BRAND_IDENTITY_PROMPT.format(
        company_name=company_name,
        brand_voice=brand_voice,
        values=format_values_list(values),
        target_audience=target_audience,
        positioning=positioning
    )
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    # Parse JSON response
    try:
        content = response.content.strip()
        if content.startswith("```json"):
            content = content.split("```json")[1].split("```")[0].strip()
        elif content.startswith("```"):
            content = content.split("```")[1].split("```")[0].strip()
        
        result = json.loads(content)
        return result
        
    except json.JSONDecodeError:
        # Fallback: return as plain text if JSON parsing fails
        return {
            "color_palette_desc": "Color palette recommendations:\n" + response.content[:500],
            "font_recommendations": "Font recommendations:\n" + response.content[500:1000],
            "messaging_guide": "Messaging guide:\n" + response.content[1000:]
        }


@retry_on_error(max_retries=3)
def generate_kpi_insights(
    base_visitors: int,
    conversion_rate: float,
    growth_rate: float,
    total_signups: int,
    brand_type: str
) -> str:
    """
    Generate AI insights about KPI projections using Gemini.
    
    Args:
        base_visitors: Starting weekly visitors
        conversion_rate: Conversion rate as percentage
        growth_rate: Weekly growth rate as percentage
        total_signups: Total projected signups over period
        brand_type: Type of brand (SaaS, D2C, etc.)
        
    Returns:
        Insights as markdown string
    """
    llm = get_llm(temperature=0.7)
    
    prompt = KPI_INSIGHTS_PROMPT.format(
        base_visitors=base_visitors,
        conversion_rate=conversion_rate,
        growth_rate=growth_rate,
        total_signups=total_signups,
        brand_type=brand_type
    )
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content.strip()


@retry_on_error(max_retries=3)
def refine_with_feedback(
    original_text: str,
    user_feedback: str,
    context: str = "brand content"
) -> str:
    """
    Refine content based on user feedback using Gemini.
    
    Args:
        original_text: The text to refine
        user_feedback: User's feedback/instructions
        context: Context about what is being refined
        
    Returns:
        Refined text as string
    """
    llm = get_llm(temperature=0.7)
    
    prompt = REFINEMENT_PROMPT.format(
        original_text=original_text,
        user_feedback=user_feedback,
        context=context
    )
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content.strip()


@retry_on_error(max_retries=3)
def generate_one_pager_copy(state: Dict) -> str:
    """
    Generate marketing one-pager copy using Gemini.
    
    Args:
        state: BrandState dictionary with all brand information
        
    Returns:
        One-pager copy as markdown string
    """
    llm = get_llm(temperature=0.7)
    
    prompt = ONE_PAGER_PROMPT.format(
        company_name=state.get("company_name", ""),
        vision=state.get("vision", ""),
        mission=state.get("mission", ""),
        target_audience=state.get("target_audience", ""),
        core_problem=state.get("core_problem", ""),
        positioning=state.get("positioning_statement", ""),
        values=format_values_list(state.get("values", []))
    )
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content.strip()


def test_api_connection() -> Dict[str, any]:
    """
    Test Gemini API connection and return diagnostics.
    
    Returns:
        Dict with status, model info, and any error messages
    """
    try:
        llm = get_llm(temperature=0.5)
        test_response = llm.invoke([HumanMessage(content="Respond with 'OK' if you can hear me.")])
        
        return {
            "status": "success",
            "message": "Gemini API connected successfully",
            "model": "gemini-2.0-flash-exp",
            "response": test_response.content,
            "api_key_present": bool(os.getenv("GOOGLE_API_KEY"))
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "model": "gemini-2.0-flash-exp",
            "api_key_present": bool(os.getenv("GOOGLE_API_KEY"))
        }


# Streaming support for real-time generation
def generate_brand_foundations_streaming(
    company_name: str,
    target_audience: str,
    core_problem: str,
    brand_voice: str,
    callback=None
):
    """
    Generate brand foundations with streaming for real-time updates.
    
    Args:
        company_name: Name of the company
        target_audience: Description of target audience
        core_problem: Problem the company solves
        brand_voice: Brand voice/tone
        callback: Optional callback function to handle streaming chunks
        
    Yields:
        Chunks of generated content as they arrive
    """
    llm = get_llm(temperature=0.7, streaming=True)
    
    prompt = FOUNDATION_PROMPT.format(
        company_name=company_name,
        target_audience=target_audience,
        core_problem=core_problem,
        brand_voice=brand_voice
    )
    
    full_response = ""
    for chunk in llm.stream([HumanMessage(content=prompt)]):
        if hasattr(chunk, 'content'):
            full_response += chunk.content
            if callback:
                callback(chunk.content)
            yield chunk.content
    
    return full_response
