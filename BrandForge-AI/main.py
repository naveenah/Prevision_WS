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
from modules.langchain_agents import (
    generate_brand_foundations,
    generate_positioning_statement,
    test_api_connection
)
from modules.workflow import (
    BrandWorkflowExecutor,
    get_workflow_progress,
    can_execute_step
)
from modules.graph_nodes import execute_node


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
    
    # Initialize workflow executor
    if "workflow_executor" not in st.session_state:
        st.session_state.workflow_executor = BrandWorkflowExecutor(use_flexible=False)


def render_sidebar():
    """Render the navigation sidebar with progress tracking."""
    with st.sidebar:
        st.title("🎨 BrandForge AI")
        st.caption("Powered by Google Gemini Pro 3")
        
        # Workflow Progress (using LangGraph tracking)
        workflow_progress = get_workflow_progress(st.session_state.brand_state)
        completion = workflow_progress["percentage"] / 100
        
        st.progress(
            completion, 
            text=f"Workflow Progress: {workflow_progress['percentage']:.0f}% ({workflow_progress['completed']}/{workflow_progress['total']} steps)"
        )
        
        # Show completed steps
        if workflow_progress["completed_steps"]:
            with st.expander("✅ Completed Steps"):
                for step in workflow_progress["completed_steps"]:
                    st.caption(f"• {step.replace('_', ' ').title()}")
        
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
        
        if st.button("� Test API Connection", use_container_width=True):
            with st.spinner("Testing Gemini API..."):
                result = test_api_connection()
                if result["status"] == "success":
                    st.success(f"✅ {result['message']}")
                else:
                    st.error(f"❌ Connection failed: {result['message']}")
                    if not result["api_key_present"]:
                        st.warning("⚠️ GOOGLE_API_KEY not found in .env file")
        
        if st.button("�🔄 Reset Workflow", use_container_width=True):
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
        "🚀 Generate with Gemini (via LangGraph)",
        disabled=not can_generate,
        use_container_width=True,
        type="primary"
    ):
        if not can_generate:
            st.error("Please fill in all required fields (marked with *)")
        else:
            with st.spinner("🤖 Gemini is analyzing your brand via LangGraph workflow..."):
                try:
                    # Check if we can execute this step
                    can_exec, message = can_execute_step("foundations", st.session_state.brand_state)
                    
                    if not can_exec:
                        st.error(f"❌ {message}")
                    else:
                        # Execute the foundations node via workflow
                        updated_state = st.session_state.workflow_executor.execute_step(
                            "foundations",
                            st.session_state.brand_state
                        )
                        
                        # Update session state with workflow results
                        st.session_state.brand_state = updated_state
                        
                        # Also execute market analysis to get positioning
                        with st.spinner("Generating positioning statement..."):
                            updated_state = st.session_state.workflow_executor.execute_step(
                                "market_analysis",
                                st.session_state.brand_state
                            )
                            st.session_state.brand_state = updated_state
                        
                        st.success("✨ Brand foundations generated successfully via LangGraph!")
                        save_state_to_file(st.session_state.brand_state)
                        st.rerun()
                    
                except ValueError as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.info("💡 Tip: Make sure your GOOGLE_API_KEY is set in the .env file")
                except Exception as e:
                    st.error(f"❌ Unexpected error: {str(e)}")
                    st.info("Please try again or check your API key configuration")
    
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
        
        # Show positioning statement if available
        if st.session_state.brand_state.get("positioning_statement"):
            st.divider()
            st.markdown("**Positioning Statement**")
            edited_positioning = st.text_area(
                "Edit positioning statement",
                value=st.session_state.brand_state["positioning_statement"],
                key="positioning_editor",
                height=100,
                label_visibility="collapsed"
            )
            st.session_state.brand_state["positioning_statement"] = edited_positioning
        
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
    st.caption("AI-powered design guidance and messaging framework")
    
    # Check if foundations are complete
    foundations_complete = all([
        st.session_state.brand_state.get("vision"),
        st.session_state.brand_state.get("mission"),
        st.session_state.brand_state.get("values")
    ])
    
    if not foundations_complete:
        st.warning("⚠️ Please complete Brand Foundations first")
        if st.button("← Go to Foundations", use_container_width=True):
            st.session_state.current_page = "foundations"
            st.rerun()
        return
    
    # Create tabs for different sections
    tabs = st.tabs(["🎨 Visual Identity", "💬 Messaging", "📄 Assets"])
    
    # ============================================================================
    # TAB 1: VISUAL IDENTITY
    # ============================================================================
    with tabs[0]:
        st.subheader("Visual Identity Guidelines")
        st.caption("Colors, typography, and design direction")
        
        # Brand voice selector (prerequisite for identity generation)
        col1, col2 = st.columns([2, 1])
        
        with col1:
            brand_voice = st.selectbox(
                "Brand Voice *",
                options=["Professional", "Friendly", "Bold", "Authoritative", "Playful", "Innovative", "Warm", "Technical"],
                index=0 if not st.session_state.brand_state.get("brand_voice") else 
                      ["Professional", "Friendly", "Bold", "Authoritative", "Playful", "Innovative", "Warm", "Technical"].index(
                          st.session_state.brand_state.get("brand_voice", "Professional")
                      ),
                help="Select the tone and personality of your brand"
            )
            st.session_state.brand_state["brand_voice"] = brand_voice
        
        with col2:
            st.metric("Completion", f"{20 if st.session_state.brand_state.get('color_palette_desc') else 0}%")
        
        st.divider()
        
        # Check if we can generate identity
        can_generate = all([
            st.session_state.brand_state.get("brand_voice"),
            st.session_state.brand_state.get("values"),
            st.session_state.brand_state.get("target_audience")
        ])
        
        # Generation button
        if st.button(
            "✨ Generate Brand Identity (via LangGraph)",
            disabled=not can_generate,
            use_container_width=True,
            type="primary"
        ):
            with st.spinner("🎨 Gemini is crafting your brand identity..."):
                try:
                    # Check prerequisites
                    can_exec, message = can_execute_step("identity", st.session_state.brand_state)
                    
                    if not can_exec:
                        st.error(f"❌ {message}")
                    else:
                        # Execute the identity node via workflow
                        updated_state = st.session_state.workflow_executor.execute_step(
                            "identity",
                            st.session_state.brand_state
                        )
                        
                        # Update session state
                        st.session_state.brand_state = updated_state
                        
                        st.success("✨ Brand identity generated successfully!")
                        save_state_to_file(st.session_state.brand_state)
                        st.rerun()
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.info("Please check your API key and try again")
        
        if not can_generate:
            st.warning("Complete brand foundations to generate identity")
        
        # Display generated identity
        if st.session_state.brand_state.get("color_palette_desc"):
            st.divider()
            
            # Color Palette
            st.markdown("### 🎨 Color Palette")
            with st.expander("View Color Recommendations", expanded=True):
                edited_colors = st.text_area(
                    "Edit color palette description",
                    value=st.session_state.brand_state["color_palette_desc"],
                    height=200,
                    key="colors_editor",
                    label_visibility="collapsed"
                )
                st.session_state.brand_state["color_palette_desc"] = edited_colors
            
            # Typography
            st.markdown("### ✍️ Typography & Fonts")
            with st.expander("View Font Recommendations", expanded=True):
                edited_fonts = st.text_area(
                    "Edit font recommendations",
                    value=st.session_state.brand_state.get("font_recommendations", ""),
                    height=200,
                    key="fonts_editor",
                    label_visibility="collapsed"
                )
                st.session_state.brand_state["font_recommendations"] = edited_fonts
            
            # Quick actions
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Regenerate Identity", use_container_width=True):
                    # Clear identity fields to force regeneration
                    st.session_state.brand_state.pop("color_palette_desc", None)
                    st.session_state.brand_state.pop("font_recommendations", None)
                    st.session_state.brand_state.pop("messaging_guide", None)
                    st.rerun()
            
            with col2:
                if st.button("💾 Save Changes", use_container_width=True):
                    save_state_to_file(st.session_state.brand_state)
                    st.success("✅ Changes saved!")
    
    # ============================================================================
    # TAB 2: MESSAGING
    # ============================================================================
    with tabs[1]:
        st.subheader("Brand Messaging Framework")
        st.caption("Voice, tone, and communication guidelines")
        
        if st.session_state.brand_state.get("messaging_guide"):
            # Display messaging guide
            st.markdown("### 📝 Your Messaging Guide")
            
            edited_messaging = st.text_area(
                "Edit messaging guidelines",
                value=st.session_state.brand_state["messaging_guide"],
                height=400,
                key="messaging_editor"
            )
            st.session_state.brand_state["messaging_guide"] = edited_messaging
            
            st.divider()
            
            # Additional messaging elements
            st.markdown("### 📢 Key Messages")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Tagline / Slogan**")
                tagline = st.text_input(
                    "tagline",
                    value=st.session_state.brand_state.get("tagline", ""),
                    placeholder="e.g., Build Brands That Matter",
                    label_visibility="collapsed"
                )
                st.session_state.brand_state["tagline"] = tagline
                
                st.markdown("**Value Proposition**")
                value_prop = st.text_area(
                    "value_prop",
                    value=st.session_state.brand_state.get("value_proposition", ""),
                    placeholder="One sentence describing your unique value...",
                    height=100,
                    label_visibility="collapsed"
                )
                st.session_state.brand_state["value_proposition"] = value_prop
            
            with col2:
                st.markdown("**Elevator Pitch (30s)**")
                elevator_pitch = st.text_area(
                    "elevator_pitch",
                    value=st.session_state.brand_state.get("elevator_pitch", ""),
                    placeholder="Brief description for quick introductions...",
                    height=150,
                    label_visibility="collapsed"
                )
                st.session_state.brand_state["elevator_pitch"] = elevator_pitch
            
            if st.button("💾 Save Messaging", use_container_width=True):
                save_state_to_file(st.session_state.brand_state)
                st.success("✅ Messaging saved!")
        
        else:
            st.info("Generate brand identity first to see messaging guidelines")
            if st.button("← Go to Visual Identity Tab"):
                st.rerun()
    
    # ============================================================================
    # TAB 3: ASSETS
    # ============================================================================
    with tabs[2]:
        st.subheader("Brand Assets & Templates")
        st.caption("Download and customize your brand materials")
        
        if not st.session_state.brand_state.get("messaging_guide"):
            st.warning("⚠️ Generate brand identity first to access downloadable assets")
        else:
            # Asset generation options
            st.markdown("### 📦 Available Assets")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📄 Brand Guide")
                st.caption("Complete brand guidelines document")
                
                if st.button("Generate Brand Guide", use_container_width=True):
                    with st.spinner("Creating comprehensive brand guide..."):
                        from modules.utils import generate_playbook_markdown
                        
                        try:
                            markdown_content = generate_playbook_markdown(st.session_state.brand_state)
                            st.session_state.brand_guide_content = markdown_content
                            st.success("✅ Brand guide generated!")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                
                # Download button for brand guide
                if st.session_state.get("brand_guide_content"):
                    st.download_button(
                        label="📥 Download Brand Guide (Markdown)",
                        data=st.session_state.brand_guide_content,
                        file_name=f"{st.session_state.brand_state.get('company_name', 'Brand')}_Guide.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
            
            with col2:
                st.markdown("#### ✉️ Email Signature")
                st.caption("Professional email signature template")
                
                # Generate email signature HTML
                company = st.session_state.brand_state.get("company_name", "Your Company")
                tagline = st.session_state.brand_state.get("tagline", "")
                
                email_signature = f"""<div style="font-family: Arial, sans-serif; font-size: 14px;">
<strong>{company}</strong><br/>
{tagline}<br/>
<a href="mailto:hello@{company.lower().replace(' ', '')}.com">hello@{company.lower().replace(' ', '')}.com</a>
</div>"""
                
                if st.button("📋 Copy Email Signature", use_container_width=True):
                    st.code(email_signature, language="html")
                    st.info("Copy the HTML above and paste into your email client")
            
            st.divider()
            
            # Complete asset package
            st.markdown("### 📦 Complete Asset Package")
            
            if st.button("🎁 Generate Complete Package (ZIP)", use_container_width=True, type="primary"):
                with st.spinner("Creating your brand asset package..."):
                    from modules.utils import create_brand_playbook_zip
                    
                    try:
                        zip_buffer = create_brand_playbook_zip(st.session_state.brand_state)
                        
                        st.download_button(
                            label="📥 Download Complete Package",
                            data=zip_buffer.getvalue(),
                            file_name=f"{st.session_state.brand_state.get('company_name', 'Brand')}_Assets.zip",
                            mime="application/zip",
                            use_container_width=True
                        )
                        
                        st.success("✅ Asset package ready for download!")
                        
                        with st.expander("📋 Package Contents"):
                            st.markdown("""
                            - `Brand_Guide.md` - Complete brand guidelines
                            - `Brand_Strategy.md` - Vision, mission, values
                            - `Visual_Identity.md` - Colors and fonts
                            - `Messaging_Guide.md` - Communication framework
                            - `Launch_Plan.csv` - 90-day roadmap (if generated)
                            - `Email_Signature.html` - Email template
                            """)
                    
                    except Exception as e:
                        st.error(f"Error creating package: {str(e)}")
    
    # Navigation footer
    st.divider()
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
