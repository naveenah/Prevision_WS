"""
BrandState Schema and State Management Utilities
Defines the core data structure for BrandForge AI workflow
"""

from typing import TypedDict, List, Dict, Optional
from datetime import datetime
import json


class BrandState(TypedDict, total=False):
    """
    Complete state schema for the BrandForge AI workflow.
    Using total=False to make all fields optional (user builds state incrementally).
    """
    
    # Step 1-3: Foundations
    company_name: str
    vision: str
    mission: str
    values: List[str]
    target_audience: str
    core_problem: str
    
    # Step 2: Research
    competitors: List[str]
    differentiation_points: str
    gap_analysis: str
    
    # Step 3-5: Identity
    positioning_statement: str
    brand_voice: str
    color_palette_desc: str
    font_recommendations: str
    
    # Step 6-9: Assets
    messaging_guide: str
    one_pager_copy: str
    email_signature: str
    
    # Step 10: Launch
    launch_start_date: str
    brand_type: str  # SaaS, D2C, Agency, E-commerce
    launch_plan_df: Dict  # Serialized DataFrame
    kpi_targets: Dict[str, float]
    
    # Metadata
    current_step: int
    last_updated: str
    workflow_complete: bool


def create_empty_state() -> BrandState:
    """
    Initialize an empty BrandState with default values.
    
    Returns:
        BrandState: A new state object with defaults
    """
    return BrandState(
        company_name="",
        vision="",
        mission="",
        values=[],
        target_audience="",
        core_problem="",
        competitors=[],
        differentiation_points="",
        gap_analysis="",
        positioning_statement="",
        brand_voice="",
        color_palette_desc="",
        font_recommendations="",
        messaging_guide="",
        one_pager_copy="",
        email_signature="",
        launch_start_date="",
        brand_type="SaaS",
        launch_plan_df={},
        kpi_targets={},
        current_step=0,
        last_updated=datetime.now().isoformat(),
        workflow_complete=False
    )


def validate_state(state: BrandState, required_fields: List[str]) -> tuple[bool, List[str]]:
    """
    Validate that required fields are present and non-empty in the state.
    
    Args:
        state: The BrandState to validate
        required_fields: List of field names that must be present
        
    Returns:
        Tuple of (is_valid, missing_fields)
    """
    missing = []
    
    for field in required_fields:
        value = state.get(field)
        
        # Check if field is missing or empty
        if value is None:
            missing.append(field)
        elif isinstance(value, str) and not value.strip():
            missing.append(field)
        elif isinstance(value, (list, dict)) and not value:
            missing.append(field)
    
    return len(missing) == 0, missing


def serialize_state(state: BrandState) -> str:
    """
    Convert BrandState to JSON string for storage.
    
    Args:
        state: The BrandState to serialize
        
    Returns:
        JSON string representation
    """
    state_copy = dict(state)
    state_copy["last_updated"] = datetime.now().isoformat()
    return json.dumps(state_copy, indent=2)


def deserialize_state(json_str: str) -> BrandState:
    """
    Convert JSON string back to BrandState.
    
    Args:
        json_str: JSON representation of state
        
    Returns:
        BrandState object
    """
    data = json.loads(json_str)
    return BrandState(**data)


def save_state_to_file(state: BrandState, filepath: str = ".brandforge_autosave.json"):
    """
    Save BrandState to local file for persistence.
    
    Args:
        state: The state to save
        filepath: Path to save file (default: .brandforge_autosave.json)
    """
    with open(filepath, "w") as f:
        f.write(serialize_state(state))


def load_state_from_file(filepath: str = ".brandforge_autosave.json") -> Optional[BrandState]:
    """
    Load BrandState from local file.
    
    Args:
        filepath: Path to saved state file
        
    Returns:
        BrandState if file exists, None otherwise
    """
    try:
        with open(filepath, "r") as f:
            return deserialize_state(f.read())
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None


def get_completion_percentage(state: BrandState) -> float:
    """
    Calculate workflow completion percentage based on filled fields.
    
    Args:
        state: The current BrandState
        
    Returns:
        Float between 0.0 and 1.0 representing completion
    """
    # Define key milestones
    milestones = {
        "foundations": ["company_name", "vision", "mission", "values", "target_audience"],
        "research": ["competitors", "gap_analysis"],
        "identity": ["brand_voice", "positioning_statement"],
        "assets": ["messaging_guide"],
        "launch": ["launch_start_date", "brand_type"]
    }
    
    total_milestones = sum(len(fields) for fields in milestones.values())
    completed = 0
    
    for fields in milestones.values():
        for field in fields:
            value = state.get(field)
            if value and (
                (isinstance(value, str) and value.strip()) or
                (isinstance(value, list) and len(value) > 0)
            ):
                completed += 1
    
    return completed / total_milestones if total_milestones > 0 else 0.0


def get_next_recommended_step(state: BrandState) -> str:
    """
    Recommend the next step based on current state completion.
    
    Args:
        state: The current BrandState
        
    Returns:
        Name of the recommended next page/step
    """
    # Check foundations
    if not state.get("vision") or not state.get("mission"):
        return "foundations"
    
    # Check research
    if not state.get("competitors") or not state.get("gap_analysis"):
        return "research"
    
    # Check identity
    if not state.get("brand_voice") or not state.get("positioning_statement"):
        return "identity"
    
    # Check launch plan
    if not state.get("launch_start_date"):
        return "launch_plan"
    
    # Check KPI setup
    if not state.get("kpi_targets"):
        return "kpi_dashboard"
    
    return "complete"


# Field descriptions for UI tooltips
FIELD_DESCRIPTIONS = {
    "company_name": "The official name of your company or brand",
    "vision": "An aspirational statement of where you want your brand to be in the future (1-2 sentences)",
    "mission": "A clear statement of what your brand does today and for whom (1-2 sentences)",
    "values": "3-5 core principles that guide your brand's decisions and culture",
    "target_audience": "Detailed description of your ideal customer (demographics, psychographics, pain points)",
    "core_problem": "The primary problem your product/service solves for your audience",
    "competitors": "List of 3-5 direct or indirect competitors in your space",
    "positioning_statement": "How you want to be perceived relative to competitors",
    "brand_voice": "The personality and tone of your brand communications (e.g., Professional, Friendly, Bold)",
    "launch_start_date": "The date you plan to officially launch your brand",
    "brand_type": "Your business model (SaaS, D2C, Agency, E-commerce, etc.)"
}
