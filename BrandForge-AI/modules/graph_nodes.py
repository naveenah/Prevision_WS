"""
LangGraph Node Functions for BrandForge AI
Defines the stateful workflow nodes that process brand building steps
"""

from typing import Dict
from modules.state import BrandState
from modules.langchain_agents import (
    generate_brand_foundations,
    generate_positioning_statement,
    analyze_competitors,
    generate_brand_identity,
    generate_kpi_insights
)
from templates.launch_plan_template import get_launch_plan_template
from modules.utils import calculate_kpi_projections
import pandas as pd
from datetime import datetime


# ============================================================================
# NODE 1: FOUNDATION PROCESSING
# ============================================================================
def node_process_foundations(state: BrandState) -> BrandState:
    """
    Process brand foundations (vision, mission, values).
    
    This node is triggered when the user has provided:
    - Company name
    - Target audience
    - Core problem
    
    Returns:
        Updated state with vision, mission, values
    """
    print("[LangGraph] Executing Node: Foundation Processing")
    
    # Generate foundations using Gemini
    result = generate_brand_foundations(
        company_name=state["company_name"],
        target_audience=state["target_audience"],
        core_problem=state["core_problem"],
        brand_voice=state.get("brand_voice", "Professional")
    )
    
    # Update state with results
    state["vision"] = result["vision"]
    state["mission"] = result["mission"]
    state["values"] = result["values"]
    state["current_step"] = 1
    state["last_updated"] = datetime.now().isoformat()
    
    print(f"[LangGraph] ✓ Foundations generated for {state['company_name']}")
    return state


# ============================================================================
# NODE 2: POSITIONING & MARKET ANALYSIS
# ============================================================================
def node_market_analysis(state: BrandState) -> BrandState:
    """
    Generate positioning statement and analyze competitive landscape.
    
    Prerequisites:
    - Brand foundations (vision, mission, values)
    - Competitors list
    - Target audience
    
    Returns:
        Updated state with positioning statement and gap analysis
    """
    print("[LangGraph] Executing Node: Market Analysis")
    
    # Generate positioning statement
    positioning = generate_positioning_statement(
        company_name=state["company_name"],
        target_audience=state["target_audience"],
        core_problem=state["core_problem"],
        brand_voice=state.get("brand_voice", "Professional"),
        values=state["values"]
    )
    state["positioning_statement"] = positioning
    
    # Analyze competitors if provided
    if state.get("competitors") and len(state["competitors"]) > 0:
        gap_analysis = analyze_competitors(
            competitors=state["competitors"],
            our_positioning=positioning,
            our_values=state["values"],
            target_audience=state["target_audience"]
        )
        state["gap_analysis"] = gap_analysis
    else:
        state["gap_analysis"] = "No competitors provided for analysis."
    
    state["current_step"] = 2
    state["last_updated"] = datetime.now().isoformat()
    
    print("[LangGraph] ✓ Market analysis completed")
    return state


# ============================================================================
# NODE 3: BRAND IDENTITY CREATION
# ============================================================================
def node_create_identity(state: BrandState) -> BrandState:
    """
    Generate complete brand identity (colors, fonts, messaging).
    
    Prerequisites:
    - Brand voice description
    - Core values
    - Target audience
    
    Returns:
        Updated state with color_palette_desc, font_recommendations, messaging_guide
    """
    print("[LangGraph] Executing Node: Identity Creation")
    
    # Generate brand identity using Gemini
    identity = generate_brand_identity(
        company_name=state["company_name"],
        brand_voice=state.get("brand_voice", "Professional and approachable"),
        values=state["values"],
        target_audience=state["target_audience"],
        positioning=state.get("positioning_statement", "")
    )
    
    # Update state with identity components
    state["color_palette_desc"] = identity["color_palette_desc"]
    state["font_recommendations"] = identity["font_recommendations"]
    state["messaging_guide"] = identity["messaging_guide"]
    state["current_step"] = 3
    state["last_updated"] = datetime.now().isoformat()
    
    print("[LangGraph] ✓ Brand identity created")
    return state


# ============================================================================
# NODE 4: LAUNCH PLAN GENERATION
# ============================================================================
def node_plan_launch(state: BrandState) -> BrandState:
    """
    Generate 90-day launch plan with week-by-week tasks.
    
    Prerequisites:
    - Brand type (SaaS, D2C, Agency, E-commerce)
    - Launch start date
    - Brand foundations
    
    Returns:
        Updated state with launch_plan_df (serialized DataFrame)
    """
    print("[LangGraph] Executing Node: Launch Planning")
    
    # Get appropriate template based on brand type
    brand_type = state.get("brand_type", "SaaS")
    template = get_launch_plan_template(brand_type)
    
    # Create DataFrame from template
    launch_df = pd.DataFrame(template)
    
    # If start date provided, calculate actual dates
    if state.get("launch_start_date"):
        from modules.utils import create_weeks_list
        start_date = state["launch_start_date"]
        weeks = create_weeks_list(start_date)
        
        # Add date ranges to DataFrame
        if len(weeks) >= len(launch_df):
            launch_df["Start Date"] = [w["start_date"] for w in weeks[:len(launch_df)]]
            launch_df["End Date"] = [w["end_date"] for w in weeks[:len(launch_df)]]
    
    # Serialize DataFrame to dict for state storage
    state["launch_plan_df"] = launch_df.to_dict('records')
    state["current_step"] = 4
    state["last_updated"] = datetime.now().isoformat()
    
    print(f"[LangGraph] ✓ Launch plan created ({len(launch_df)} weeks)")
    return state


# ============================================================================
# NODE 5: KPI CALCULATION & INSIGHTS
# ============================================================================
def node_calculate_kpis(state: BrandState) -> BrandState:
    """
    Calculate KPI projections and generate AI insights.
    
    Prerequisites:
    - Launch plan DataFrame
    - KPI targets (optional)
    
    Returns:
        Updated state with kpi_projections and kpi_insights
    """
    print("[LangGraph] Executing Node: KPI Calculation")
    
    # Default KPI targets if not provided
    if not state.get("kpi_targets"):
        state["kpi_targets"] = {
            "weekly_traffic_growth": 15.0,
            "conversion_rate": 2.5,
            "email_open_rate": 25.0,
            "social_engagement_rate": 5.0,
            "customer_acquisition_cost": 50.0
        }
    
    # Calculate projections
    projections = calculate_kpi_projections(
        weeks=13,  # 90 days / 7 = ~13 weeks
        targets=state["kpi_targets"]
    )
    
    # Generate AI insights about the projections
    insights = generate_kpi_insights(
        projections=projections,
        targets=state["kpi_targets"],
        brand_type=state.get("brand_type", "SaaS")
    )
    
    state["kpi_projections"] = projections
    state["kpi_insights"] = insights
    state["current_step"] = 5
    state["last_updated"] = datetime.now().isoformat()
    
    print("[LangGraph] ✓ KPI calculations completed")
    return state


# ============================================================================
# CONDITIONAL ROUTING LOGIC
# ============================================================================
def should_analyze_competitors(state: BrandState) -> str:
    """
    Decide whether to run competitor analysis based on data availability.
    
    Returns:
        "analyze" if competitors provided, "skip" otherwise
    """
    if state.get("competitors") and len(state["competitors"]) > 0:
        return "analyze"
    return "skip"


def needs_identity_update(state: BrandState) -> str:
    """
    Check if brand identity needs regeneration.
    
    Returns:
        "generate" if identity missing or brand_voice changed, "skip" otherwise
    """
    if not state.get("color_palette_desc") or not state.get("font_recommendations"):
        return "generate"
    return "skip"


# ============================================================================
# HELPER: EXECUTE SINGLE NODE
# ============================================================================
def execute_node(node_name: str, state: BrandState) -> BrandState:
    """
    Execute a single node by name.
    
    Args:
        node_name: Name of node to execute
        state: Current brand state
        
    Returns:
        Updated state
    """
    nodes = {
        "foundations": node_process_foundations,
        "market_analysis": node_market_analysis,
        "identity": node_create_identity,
        "launch_plan": node_plan_launch,
        "kpis": node_calculate_kpis
    }
    
    if node_name not in nodes:
        raise ValueError(f"Unknown node: {node_name}")
    
    return nodes[node_name](state)
