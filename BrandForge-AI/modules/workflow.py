"""
LangGraph Workflow Definition for BrandForge AI
Creates and manages the stateful brand-building workflow
"""

from typing import Dict, Literal
from langgraph.graph import StateGraph, END
from modules.state import BrandState
from modules.graph_nodes import (
    node_process_foundations,
    node_market_analysis,
    node_create_identity,
    node_plan_launch,
    node_calculate_kpis
)


# ============================================================================
# WORKFLOW COMPILATION
# ============================================================================
def create_brand_workflow() -> StateGraph:
    """
    Create and compile the LangGraph workflow for brand building.
    
    Workflow Structure:
    
    START → foundations → market_analysis → identity → launch_plan → kpis → END
    
    Each node can be executed independently for human-in-the-loop control.
    
    Returns:
        Compiled StateGraph ready for execution
    """
    # Initialize the graph with BrandState schema
    workflow = StateGraph(BrandState)
    
    # Add all processing nodes
    workflow.add_node("foundations", node_process_foundations)
    workflow.add_node("market_analysis", node_market_analysis)
    workflow.add_node("identity", node_create_identity)
    workflow.add_node("launch_plan", node_plan_launch)
    workflow.add_node("kpis", node_calculate_kpis)
    
    # Define the workflow edges (sequential flow)
    workflow.set_entry_point("foundations")
    workflow.add_edge("foundations", "market_analysis")
    workflow.add_edge("market_analysis", "identity")
    workflow.add_edge("identity", "launch_plan")
    workflow.add_edge("launch_plan", "kpis")
    workflow.add_edge("kpis", END)
    
    # Compile the graph
    return workflow.compile()


# ============================================================================
# FLEXIBLE WORKFLOW WITH CONDITIONAL ROUTING (Advanced)
# ============================================================================
def create_flexible_workflow() -> StateGraph:
    """
    Create a more flexible workflow with conditional routing.
    
    This version allows skipping optional steps based on data availability.
    
    Workflow Structure:
    
    START → foundations → check_competitors
              ↓
         market_analysis (if competitors provided)
              ↓
         check_identity
              ↓
         identity (if brand_voice changed)
              ↓
         launch_plan → kpis → END
    
    Returns:
        Compiled StateGraph with conditional routing
    """
    workflow = StateGraph(BrandState)
    
    # Add nodes
    workflow.add_node("foundations", node_process_foundations)
    workflow.add_node("market_analysis", node_market_analysis)
    workflow.add_node("identity", node_create_identity)
    workflow.add_node("launch_plan", node_plan_launch)
    workflow.add_node("kpis", node_calculate_kpis)
    
    # Conditional routing functions
    def route_after_foundations(state: BrandState) -> Literal["market_analysis", "identity"]:
        """Route to market analysis if competitors provided, else skip to identity."""
        if state.get("competitors") and len(state["competitors"]) > 0:
            return "market_analysis"
        return "identity"
    
    def route_after_market(state: BrandState) -> Literal["identity"]:
        """Always proceed to identity after market analysis."""
        return "identity"
    
    # Set entry point
    workflow.set_entry_point("foundations")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "foundations",
        route_after_foundations,
        {
            "market_analysis": "market_analysis",
            "identity": "identity"
        }
    )
    
    workflow.add_edge("market_analysis", "identity")
    workflow.add_edge("identity", "launch_plan")
    workflow.add_edge("launch_plan", "kpis")
    workflow.add_edge("kpis", END)
    
    return workflow.compile()


# ============================================================================
# HUMAN-IN-THE-LOOP WORKFLOW EXECUTOR
# ============================================================================
class BrandWorkflowExecutor:
    """
    Manages workflow execution with human-in-the-loop control.
    
    This class allows:
    - Step-by-step execution
    - Pausing after each node
    - Manual edits between steps
    - Jumping to specific steps
    """
    
    def __init__(self, use_flexible: bool = False):
        """
        Initialize the workflow executor.
        
        Args:
            use_flexible: Use flexible workflow with conditional routing
        """
        if use_flexible:
            self.workflow = create_flexible_workflow()
        else:
            self.workflow = create_brand_workflow()
        
        self.current_state = None
        self.execution_history = []
    
    def execute_step(self, step_name: str, state: BrandState) -> BrandState:
        """
        Execute a single step in the workflow.
        
        Args:
            step_name: Name of the step/node to execute
            state: Current brand state
            
        Returns:
            Updated state after step execution
        """
        print(f"\n[Workflow] Executing step: {step_name}")
        
        # Map step names to node names
        step_mapping = {
            "foundations": "foundations",
            "market_analysis": "market_analysis",
            "positioning": "market_analysis",
            "identity": "identity",
            "launch_plan": "launch_plan",
            "kpis": "kpis"
        }
        
        node_name = step_mapping.get(step_name, step_name)
        
        # Execute the specific node
        from modules.graph_nodes import execute_node
        updated_state = execute_node(node_name, state)
        
        # Track execution
        self.execution_history.append({
            "step": step_name,
            "timestamp": updated_state.get("last_updated")
        })
        
        self.current_state = updated_state
        return updated_state
    
    def execute_full_workflow(self, initial_state: BrandState) -> BrandState:
        """
        Execute the complete workflow from start to finish.
        
        Args:
            initial_state: Starting brand state with required inputs
            
        Returns:
            Final state after all nodes executed
        """
        print("\n[Workflow] Starting full workflow execution...")
        
        # Invoke the compiled graph
        final_state = self.workflow.invoke(initial_state)
        
        self.current_state = final_state
        print("[Workflow] ✓ Full workflow completed")
        
        return final_state
    
    def get_next_step(self, current_step: int) -> str:
        """
        Determine the next step based on current progress.
        
        Args:
            current_step: Current step number (0-5)
            
        Returns:
            Name of next step to execute
        """
        steps = [
            "foundations",      # 0
            "market_analysis",  # 1
            "identity",         # 2
            "launch_plan",      # 3
            "kpis"             # 4
        ]
        
        if current_step < len(steps) - 1:
            return steps[current_step + 1]
        return None  # Workflow complete
    
    def reset(self):
        """Reset the executor state."""
        self.current_state = None
        self.execution_history = []


# ============================================================================
# STREAMLIT INTEGRATION HELPERS
# ============================================================================
def get_workflow_progress(state: BrandState) -> Dict:
    """
    Calculate workflow completion progress.
    
    Args:
        state: Current brand state
        
    Returns:
        Dict with progress metrics
    """
    required_fields = {
        "foundations": ["vision", "mission", "values"],
        "market_analysis": ["positioning_statement"],
        "identity": ["color_palette_desc", "font_recommendations", "messaging_guide"],
        "launch_plan": ["launch_plan_df"],
        "kpis": ["kpi_projections"]
    }
    
    completed_steps = []
    for step, fields in required_fields.items():
        if all(state.get(field) for field in fields):
            completed_steps.append(step)
    
    total_steps = len(required_fields)
    completed = len(completed_steps)
    
    return {
        "total": total_steps,
        "completed": completed,
        "percentage": (completed / total_steps) * 100,
        "completed_steps": completed_steps,
        "current_step": state.get("current_step", 0)
    }


def can_execute_step(step_name: str, state: BrandState) -> tuple[bool, str]:
    """
    Check if a step can be executed based on prerequisites.
    
    Args:
        step_name: Name of step to check
        state: Current brand state
        
    Returns:
        Tuple of (can_execute: bool, message: str)
    """
    prerequisites = {
        "foundations": {
            "fields": ["company_name", "target_audience", "core_problem"],
            "message": "Please provide company name, target audience, and core problem"
        },
        "market_analysis": {
            "fields": ["vision", "mission", "values"],
            "message": "Complete brand foundations first"
        },
        "identity": {
            "fields": ["vision", "mission", "values"],
            "message": "Complete brand foundations first"
        },
        "launch_plan": {
            "fields": ["vision", "mission", "brand_type"],
            "message": "Complete foundations and select brand type"
        },
        "kpis": {
            "fields": ["launch_plan_df"],
            "message": "Generate launch plan first"
        }
    }
    
    if step_name not in prerequisites:
        return True, ""
    
    prereqs = prerequisites[step_name]
    missing_fields = [f for f in prereqs["fields"] if not state.get(f)]
    
    if missing_fields:
        return False, prereqs["message"]
    
    return True, ""
