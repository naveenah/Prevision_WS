"""
BrandForge AI - Main Application
A Streamlit app for guiding founders through brand building using LangGraph and Google Gemini
"""

import streamlit as st
from datetime import datetime
import sys
from pathlib import Path

# Add modules to path
sys.path.append(str(Path(__file__).parent))

from modules.state import (
    BrandState,
    create_empty_state,
    get_completion_percentage,
    get_next_recommended_step,
    save_state_to_file,
    load_state_from_file,
    FIELD_DESCRIPTIONS
)
from modules.utils import calculate_workflow_statistics


# Page Configuration
st.set_page_config(
    page_title="BrandForge AI",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)


def initialize_session_state():
    """Initialize Streamlit session state with BrandState."""
    if "brand_state" not in st.session_state:
        # Try to load saved state
        saved_state = load_state_from_file()
        
        if saved_state:
            st.session_state.brand_state = saved_state
            st.session_state.resumed = True
        else:
            st.session_state.brand_state = create_empty_state()
            st.session_state.resumed = False
    
    # Initialize other session variables
    if "current_page" not in st.session_state:
        st.session_state.current_page = "foundations"
    
    if "auto_save_enabled" not in st.session_state:
        st.session_state.auto_save_enabled = True


def render_sidebar():
    """Render the navigation sidebar with progress tracking."""
    with st.sidebar:
        st.title("🎨 BrandForge AI")
        st.caption("Powered by Google Gemini Pro 3")
        
        # Progress Bar
        completion = get_completion_percentage(st.session_state.brand_state)
        st.progress(completion, text=f"Workflow Progress: {completion*100:.0f}%")
        
        st.divider()
        
        # Navigation
        st.subheader("📍 Navigation")
        
        pages = {
            "foundations": "🎯 Brand Foundations",
            "identity": "🎨 Identity & Assets",
            "launch_plan": "📅 90-Day Launch Plan",
            "kpi_dashboard": "📊 KPI Dashboard"
        }
        
        # Highlight current page
        for page_key, page_label in pages.items():
            if st.button(
                page_label,
                key=f"nav_{page_key}",
                use_container_width=True,
                type="primary" if st.session_state.current_page == page_key else "secondary"
            ):
                st.session_state.current_page = page_key
                st.rerun()
        
        st.divider()
        
        # Quick Stats
        st.subheader("📈 Quick Stats")
        stats = calculate_workflow_statistics(st.session_state.brand_state)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Fields Filled", f"{stats['filled_fields']}/{stats['total_fields']}")
        with col2:
            st.metric("Step", stats['current_step'])
        
        st.divider()
        
        # Actions
        st.subheader("⚙️ Actions")
        
        if st.button("💾 Save Progress", use_container_width=True):
            save_state_to_file(st.session_state.brand_state)
            st.success("Progress saved!")
        
        if st.button("🔄 Reset Workflow", use_container_width=True):
            if st.session_state.get("confirm_reset", False):
                st.session_state.brand_state = create_empty_state()
                st.session_state.current_page = "foundations"
                st.session_state.confirm_reset = False
                st.success("Workflow reset!")
                st.rerun()
            else:
                st.session_state.confirm_reset = True
                st.warning("Click again to confirm reset")
        
        st.divider()
        
        # Footer
        st.caption(f"Last updated: {datetime.now().strftime('%I:%M %p')}")
        st.caption("v0.1.0 | December 2025")


def page_foundations():
    """Brand Foundations page - Step 1-3."""
    st.header("🎯 Brand Foundations")
    st.caption("Define your vision, mission, and core values")
    
    # Show resume message if applicable
    if st.session_state.get("resumed", False):
        st.info("✅ Previous session restored. Continue where you left off!")
        st.session_state.resumed = False
    
    # Input Section
    st.subheader("📝 Tell Us About Your Brand")
    
    col1, col2 = st.columns(2)
    
    with col1:
        company_name = st.text_input(
            "Company Name *",
            value=st.session_state.brand_state.get("company_name", ""),
            placeholder="e.g., BrandForge AI",
            help=FIELD_DESCRIPTIONS["company_name"]
        )
        if company_name:
            st.session_state.brand_state["company_name"] = company_name
        
        target_audience = st.text_area(
            "Who do you serve? *",
            value=st.session_state.brand_state.get("target_audience", ""),
            placeholder="e.g., Early-stage founders building consumer brands...",
            help=FIELD_DESCRIPTIONS["target_audience"],
            height=150
        )
        if target_audience:
            st.session_state.brand_state["target_audience"] = target_audience
    
    with col2:
        core_problem = st.text_area(
            "What problem do you solve? *",
            value=st.session_state.brand_state.get("core_problem", ""),
            placeholder="e.g., Founders lack structured guidance for brand development...",
            help=FIELD_DESCRIPTIONS["core_problem"],
            height=150
        )
        if core_problem:
            st.session_state.brand_state["core_problem"] = core_problem
        
        brand_voice = st.selectbox(
            "Brand Voice *",
            options=["", "Professional", "Friendly", "Bold", "Authoritative", "Playful", "Innovative"],
            index=0 if not st.session_state.brand_state.get("brand_voice") else 
                  ["", "Professional", "Friendly", "Bold", "Authoritative", "Playful", "Innovative"].index(
                      st.session_state.brand_state["brand_voice"]
                  ),
            help=FIELD_DESCRIPTIONS["brand_voice"]
        )
        if brand_voice:
            st.session_state.brand_state["brand_voice"] = brand_voice
    
    st.divider()
    
    # Generation Section
    st.subheader("✨ AI-Generated Brand Core")
    
    # Check if required fields are filled
    can_generate = all([
        st.session_state.brand_state.get("company_name"),
        st.session_state.brand_state.get("target_audience"),
        st.session_state.brand_state.get("core_problem")
    ])
    
    if st.button(
        "🚀 Generate with Gemini",
        disabled=not can_generate,
        use_container_width=True,
        type="primary"
    ):
        if not can_generate:
            st.error("Please fill in all required fields (marked with *)")
        else:
            with st.spinner("🤖 Gemini is analyzing your brand..."):
                # TODO: Implement Gemini API call in Phase 2
                # For now, show placeholder
                st.info("⚠️ AI generation will be implemented in Phase 2")
                
                # Placeholder values
                st.session_state.brand_state["vision"] = "Your AI-generated vision statement will appear here..."
                st.session_state.brand_state["mission"] = "Your AI-generated mission statement will appear here..."
                st.session_state.brand_state["values"] = [
                    "Innovation: Pushing boundaries",
                    "Integrity: Building trust",
                    "Impact: Creating value"
                ]
                st.session_state.brand_state["current_step"] = 1
    
    if not can_generate:
        st.warning("Fill in all required fields above to generate AI recommendations")
    
    # Display Generated Results
    if st.session_state.brand_state.get("vision"):
        st.divider()
        st.subheader("📄 Your Brand Core")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Vision Statement**")
            edited_vision = st.text_area(
                "Edit if needed",
                value=st.session_state.brand_state["vision"],
                key="vision_editor",
                height=120,
                label_visibility="collapsed"
            )
            st.session_state.brand_state["vision"] = edited_vision
        
        with col2:
            st.markdown("**Mission Statement**")
            edited_mission = st.text_area(
                "Edit if needed",
                value=st.session_state.brand_state["mission"],
                key="mission_editor",
                height=120,
                label_visibility="collapsed"
            )
            st.session_state.brand_state["mission"] = edited_mission
        
        st.markdown("**Core Values**")
        values_text = st.text_area(
            "Edit values (one per line)",
            value="\n".join(st.session_state.brand_state.get("values", [])),
            key="values_editor",
            height=100,
            label_visibility="collapsed"
        )
        st.session_state.brand_state["values"] = [v.strip() for v in values_text.split("\n") if v.strip()]
        
        # Next Steps
        st.divider()
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("Continue to Identity & Assets →", use_container_width=True, type="primary"):
                st.session_state.current_page = "identity"
                save_state_to_file(st.session_state.brand_state)
                st.rerun()


def page_identity():
    """Brand Identity & Assets page."""
    st.header("🎨 Brand Identity & Assets")
    st.caption("Visual identity and messaging guidelines")
    
    # Coming soon message
    st.info("🚧 This page will be implemented in Phase 5")
    
    st.markdown("""
    ### What's Coming:
    - 🎨 AI-generated color palette recommendations
    - ✍️ Font pairing suggestions
    - 📝 Brand messaging guide
    - 📄 One-pager copy generation
    - ✉️ Email signature templates
    """)
    
    # Navigation
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Foundations", use_container_width=True):
            st.session_state.current_page = "foundations"
            st.rerun()
    with col2:
        if st.button("Continue to Launch Plan →", use_container_width=True):
            st.session_state.current_page = "launch_plan"
            st.rerun()


def page_launch_plan():
    """90-Day Launch Plan page."""
    st.header("📅 90-Day Launch Plan")
    st.caption("Your week-by-week roadmap to launch")
    
    # Coming soon message
    st.info("🚧 This page will be implemented in Phase 6")
    
    st.markdown("""
    ### What's Coming:
    - 📊 Interactive 90-day calendar
    - ✏️ Editable task lists
    - 📥 CSV export for project management tools
    - 🤖 AI-customized recommendations based on your brand type
    """)
    
    # Navigation
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Identity", use_container_width=True):
            st.session_state.current_page = "identity"
            st.rerun()
    with col2:
        if st.button("Continue to KPI Dashboard →", use_container_width=True):
            st.session_state.current_page = "kpi_dashboard"
            st.rerun()


def page_kpi_dashboard():
    """KPI Dashboard Simulator page."""
    st.header("📊 KPI Dashboard Simulator")
    st.caption("Project your launch metrics and track progress")
    
    # Coming soon message
    st.info("🚧 This page will be implemented in Phase 7")
    
    st.markdown("""
    ### What's Coming:
    - 📈 Interactive KPI projections
    - 🎯 Goal setting tools
    - 📊 Visual charts and graphs
    - 🤖 AI-powered insights and recommendations
    - 📋 Google Sheets formulas generator
    """)
    
    # Navigation
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Launch Plan", use_container_width=True):
            st.session_state.current_page = "launch_plan"
            st.rerun()
    with col2:
        if st.button("Download Playbook 📦", use_container_width=True, type="primary"):
            st.info("Playbook export will be available in Phase 8")


def main():
    """Main application entry point."""
    # Initialize session state
    initialize_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Route to appropriate page
    page_router = {
        "foundations": page_foundations,
        "identity": page_identity,
        "launch_plan": page_launch_plan,
        "kpi_dashboard": page_kpi_dashboard
    }
    
    current_page = st.session_state.current_page
    page_function = page_router.get(current_page, page_foundations)
    page_function()
    
    # Auto-save (every interaction)
    if st.session_state.get("auto_save_enabled", True):
        save_state_to_file(st.session_state.brand_state)


if __name__ == "__main__":
    main()
