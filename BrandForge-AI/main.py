"""
BrandForge AI - Main Application
A Streamlit app for guiding founders through brand building using LangGraph and Google Gemini
"""

import streamlit as st
from datetime import datetime
import sys
from pathlib import Path
import pandas as pd

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
    test_api_connection,
    refine_content_with_feedback,
    generate_alternative_versions,
    compare_versions
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
        
        # Complete Playbook Export (New Phase 7 feature)
        if workflow_progress["percentage"] >= 75:  # At least 75% complete
            st.markdown("**📦 Export Complete Playbook**")
            if st.button("📥 Download Everything", use_container_width=True, type="primary"):
                with st.spinner("Preparing your complete brand playbook..."):
                    try:
                        # Gather all data
                        state = st.session_state.brand_state
                        
                        # Get launch plan if exists
                        launch_df = None
                        if state.get("launch_plan_df"):
                            launch_df = pd.DataFrame(state["launch_plan_df"])
                        
                        # Get KPI projections if exists
                        kpi_df = None
                        if state.get("kpi_projections"):
                            kpi_df = pd.DataFrame(state["kpi_projections"])
                        
                        # Create ZIP package
                        from modules.utils import create_brand_playbook_zip
                        zip_buffer = create_brand_playbook_zip(state, launch_df, kpi_df)
                        
                        # Provide download
                        st.download_button(
                            label="💾 Download Complete Package",
                            data=zip_buffer,
                            file_name=f"{state['company_name']}_BrandPlaybook.zip",
                            mime="application/zip",
                            use_container_width=True
                        )
                        st.success("✅ Package ready! Click above to download.")
                    except Exception as e:
                        st.error(f"Error creating package: {str(e)}")
            
            st.divider()
        
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
        
        # ===== PHASE 8: AI REFINEMENT SECTION =====
        st.divider()
        st.subheader("✨ AI Refinement Tools")
        st.caption("Not quite right? Get AI-powered refinements based on your feedback")
        
        # Refinement tabs
        refine_tab1, refine_tab2, refine_tab3 = st.tabs(["🔄 Refine with Feedback", "🎯 Generate Alternatives", "📊 Version History"])
        
        with refine_tab1:
            st.markdown("**Refine Content with Your Feedback**")
            
            # Select field to refine
            refine_field = st.selectbox(
                "What would you like to refine?",
                options=["Vision Statement", "Mission Statement", "Positioning Statement", "Values (all)"],
                key="refine_field_selector"
            )
            
            # Show current content
            field_mapping = {
                "Vision Statement": ("vision", "vision"),
                "Mission Statement": ("mission", "mission"),
                "Positioning Statement": ("positioning_statement", "positioning statement"),
                "Values (all)": ("values", "core values")
            }
            
            state_key, display_name = field_mapping[refine_field]
            current_content = st.session_state.brand_state.get(state_key, "")
            
            if isinstance(current_content, list):
                current_content = "\n".join(current_content)
            
            st.info(f"**Current {display_name}:**\n\n{current_content}")
            
            # Feedback input
            user_feedback = st.text_area(
                "What would you like to change or improve?",
                placeholder="Example: Make it more aspirational and less generic, or focus more on the environmental impact",
                key="refine_feedback_input",
                height=80
            )
            
            # Refine button
            col1, col2 = st.columns([2, 1])
            with col1:
                if st.button("🚀 Refine with Gemini", use_container_width=True, type="primary", disabled=not user_feedback):
                    if user_feedback:
                        with st.spinner(f"🤖 Gemini is refining your {display_name}..."):
                            try:
                                context = f"{st.session_state.brand_state.get('company_name')} - {st.session_state.brand_state.get('target_audience')}"
                                
                                refined = refine_content_with_feedback(
                                    original_text=current_content,
                                    user_feedback=user_feedback,
                                    context=context,
                                    field_name=display_name
                                )
                                
                                # Show comparison
                                st.success("✨ Refinement complete!")
                                
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    st.markdown("**Before:**")
                                    st.text_area("", value=current_content, height=120, disabled=True, key="before_refine", label_visibility="collapsed")
                                with col_b:
                                    st.markdown("**After:**")
                                    st.text_area("", value=refined, height=120, disabled=True, key="after_refine", label_visibility="collapsed")
                                
                                # Stats
                                comparison = compare_versions(current_content, refined, context)
                                st.caption(f"📊 Length: {comparison['word_count_original']} → {comparison['word_count_refined']} words ({comparison['length_change_pct']:+.0f}%)")
                                
                                # Apply button
                                if st.button("✅ Apply This Version", use_container_width=True, key="apply_refined"):
                                    if state_key == "values":
                                        st.session_state.brand_state[state_key] = [v.strip() for v in refined.split("\n") if v.strip()]
                                    else:
                                        st.session_state.brand_state[state_key] = refined
                                    
                                    # Track version history
                                    if "refinement_history" not in st.session_state.brand_state:
                                        st.session_state.brand_state["refinement_history"] = []
                                    
                                    st.session_state.brand_state["refinement_history"].append({
                                        "field": state_key,
                                        "original": current_content,
                                        "refined": refined,
                                        "feedback": user_feedback,
                                        "timestamp": datetime.now().isoformat()
                                    })
                                    
                                    save_state_to_file(st.session_state.brand_state)
                                    st.success("✅ Applied! The content has been updated.")
                                    st.rerun()
                                    
                            except Exception as e:
                                st.error(f"❌ Error during refinement: {str(e)}")
            
            with col2:
                st.caption("💡 Be specific with your feedback for best results")
        
        with refine_tab2:
            st.markdown("**Generate Alternative Versions**")
            st.caption("Get 3 different versions to choose from")
            
            # Select field for alternatives
            alt_field = st.selectbox(
                "Generate alternatives for:",
                options=["Vision Statement", "Mission Statement", "Positioning Statement"],
                key="alt_field_selector"
            )
            
            field_map = {
                "Vision Statement": "vision",
                "Mission Statement": "mission",
                "Positioning Statement": "positioning_statement"
            }
            
            alt_state_key = field_map[alt_field]
            alt_current = st.session_state.brand_state.get(alt_state_key, "")
            
            st.info(f"**Current:** {alt_current}")
            
            if st.button("🎲 Generate 3 Alternatives", use_container_width=True, type="primary"):
                with st.spinner("🤖 Gemini is creating alternatives..."):
                    try:
                        context = f"{st.session_state.brand_state.get('company_name')} - {st.session_state.brand_state.get('target_audience')}"
                        
                        alternatives = generate_alternative_versions(
                            original_text=alt_current,
                            context=context,
                            field_name=alt_field,
                            num_versions=3
                        )
                        
                        st.success(f"✨ Generated {len(alternatives)} alternatives!")
                        
                        for i, alt in enumerate(alternatives, 1):
                            with st.container():
                                st.markdown(f"**Option {i}:**")
                                st.write(alt)
                                
                                if st.button(f"✅ Use Option {i}", key=f"use_alt_{i}", use_container_width=True):
                                    st.session_state.brand_state[alt_state_key] = alt
                                    
                                    # Track in history
                                    if "refinement_history" not in st.session_state.brand_state:
                                        st.session_state.brand_state["refinement_history"] = []
                                    
                                    st.session_state.brand_state["refinement_history"].append({
                                        "field": alt_state_key,
                                        "original": alt_current,
                                        "refined": alt,
                                        "feedback": f"Selected alternative version {i}",
                                        "timestamp": datetime.now().isoformat()
                                    })
                                    
                                    save_state_to_file(st.session_state.brand_state)
                                    st.success(f"✅ Applied Option {i}!")
                                    st.rerun()
                                
                                st.divider()
                    
                    except Exception as e:
                        st.error(f"❌ Error generating alternatives: {str(e)}")
        
        with refine_tab3:
            st.markdown("**Refinement History**")
            
            history = st.session_state.brand_state.get("refinement_history", [])
            
            if not history:
                st.info("No refinements yet. Use the tabs above to start refining your content!")
            else:
                st.caption(f"Total refinements: {len(history)}")
                
                for i, entry in enumerate(reversed(history[-10:]), 1):  # Show last 10
                    with st.expander(f"🔄 {entry['field'].replace('_', ' ').title()} - {entry.get('timestamp', 'N/A')[:16]}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**Before:**")
                            st.text(entry['original'][:200] + ("..." if len(entry['original']) > 200 else ""))
                        with col2:
                            st.markdown("**After:**")
                            st.text(entry['refined'][:200] + ("..." if len(entry['refined']) > 200 else ""))
                        
                        st.caption(f"**Feedback:** {entry.get('feedback', 'N/A')}")
                        
                        # Restore button
                        if st.button(f"↶ Restore This Version", key=f"restore_{i}"):
                            field_key = entry['field']
                            if field_key == "values":
                                st.session_state.brand_state[field_key] = [v.strip() for v in entry['refined'].split("\n") if v.strip()]
                            else:
                                st.session_state.brand_state[field_key] = entry['refined']
                            save_state_to_file(st.session_state.brand_state)
                            st.success("✅ Version restored!")
                            st.rerun()
        
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
            
            # ===== PHASE 8: REFINEMENT FOR IDENTITY CONTENT =====
            st.divider()
            st.subheader("✨ Refine Your Messaging")
            st.caption("Use AI to improve your brand voice and messaging")
            
            with st.expander("🔄 Refine Messaging Content", expanded=False):
                # Select what to refine
                identity_field = st.selectbox(
                    "What would you like to refine?",
                    options=["Messaging Guide", "Tagline", "Value Proposition", "Elevator Pitch"],
                    key="identity_refine_selector"
                )
                
                field_key_map = {
                    "Messaging Guide": "messaging_guide",
                    "Tagline": "tagline",
                    "Value Proposition": "value_proposition",
                    "Elevator Pitch": "elevator_pitch"
                }
                
                selected_key = field_key_map[identity_field]
                current_value = st.session_state.brand_state.get(selected_key, "")
                
                if current_value:
                    st.info(f"**Current {identity_field}:**\n\n{current_value[:300]}{'...' if len(current_value) > 300 else ''}")
                    
                    # Feedback input
                    identity_feedback = st.text_area(
                        "What improvements would you like?",
                        placeholder="Example: Make it more concise, emphasize the innovation aspect, use simpler language",
                        key="identity_feedback_input",
                        height=80
                    )
                    
                    if st.button("🚀 Refine with Gemini", use_container_width=True, type="primary", disabled=not identity_feedback, key="refine_identity_btn"):
                        if identity_feedback:
                            with st.spinner(f"🤖 Refining your {identity_field}..."):
                                try:
                                    context = f"{st.session_state.brand_state.get('company_name')} - Brand identity content"
                                    
                                    refined = refine_content_with_feedback(
                                        original_text=current_value,
                                        user_feedback=identity_feedback,
                                        context=context,
                                        field_name=identity_field
                                    )
                                    
                                    # Show comparison
                                    st.success("✨ Refinement complete!")
                                    
                                    col_a, col_b = st.columns(2)
                                    with col_a:
                                        st.markdown("**Before:**")
                                        st.text_area("", value=current_value, height=150, disabled=True, key="identity_before", label_visibility="collapsed")
                                    with col_b:
                                        st.markdown("**After:**")
                                        st.text_area("", value=refined, height=150, disabled=True, key="identity_after", label_visibility="collapsed")
                                    
                                    # Apply button
                                    if st.button("✅ Apply Refined Version", use_container_width=True, key="apply_identity_refined"):
                                        st.session_state.brand_state[selected_key] = refined
                                        
                                        # Track in history
                                        if "refinement_history" not in st.session_state.brand_state:
                                            st.session_state.brand_state["refinement_history"] = []
                                        
                                        st.session_state.brand_state["refinement_history"].append({
                                            "field": selected_key,
                                            "original": current_value,
                                            "refined": refined,
                                            "feedback": identity_feedback,
                                            "timestamp": datetime.now().isoformat()
                                        })
                                        
                                        save_state_to_file(st.session_state.brand_state)
                                        st.success("✅ Applied! Content updated.")
                                        st.rerun()
                                        
                                except Exception as e:
                                    st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning(f"No {identity_field} found. Please complete the field first.")
        
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
    
    state = st.session_state.brand_state
    executor = st.session_state.workflow_executor
    
    # Check prerequisites
    if not state.get("company_name"):
        st.warning("⚠️ Please complete the Brand Foundations page first.")
        if st.button("Go to Foundations →"):
            st.session_state.current_page = "foundations"
            st.rerun()
        return
    
    # Check if launch plan exists
    has_launch_plan = state.get("launch_plan_df") is not None
    
    # Configuration Section
    st.subheader("🎯 Launch Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Brand Type Selection
        brand_type_options = ["SaaS", "D2C", "Agency", "E-commerce"]
        current_brand_type = state.get("brand_type", "SaaS")
        brand_type = st.selectbox(
            "Brand Type",
            options=brand_type_options,
            index=brand_type_options.index(current_brand_type) if current_brand_type in brand_type_options else 0,
            help="Select your brand type to get a customized launch plan"
        )
        
        # Update state if changed
        if brand_type != state.get("brand_type"):
            state["brand_type"] = brand_type
            save_state_to_file(state)
    
    with col2:
        # Launch Start Date
        from datetime import date, timedelta
        default_date = date.today() + timedelta(days=7)
        
        current_start_date = state.get("launch_start_date")
        if current_start_date:
            try:
                start_date_obj = date.fromisoformat(current_start_date)
            except:
                start_date_obj = default_date
        else:
            start_date_obj = default_date
        
        start_date = st.date_input(
            "Launch Start Date",
            value=start_date_obj,
            help="When do you plan to begin executing your launch plan?"
        )
        
        # Update state if changed
        start_date_str = start_date.strftime("%Y-%m-%d")
        if start_date_str != state.get("launch_start_date"):
            state["launch_start_date"] = start_date_str
            save_state_to_file(state)
    
    st.markdown("---")
    
    # Generate Launch Plan Button
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if not has_launch_plan:
            st.info("💡 Click the button to generate your customized 90-day launch plan")
        else:
            st.success("✅ Launch plan generated! You can regenerate it anytime to apply configuration changes.")
    
    with col2:
        if st.button("🤖 Generate Plan", type="primary", use_container_width=True):
            with st.spinner("Generating your 90-day launch plan..."):
                try:
                    # Execute the launch plan node
                    updated_state = executor.execute_step("launch_plan", state)
                    
                    # Update session state with new launch plan
                    st.session_state.brand_state = updated_state
                    save_state_to_file(updated_state)
                    st.success("🎉 Launch plan generated successfully!")
                    st.rerun()
                
                except Exception as e:
                    st.error(f"Error generating launch plan: {str(e)}")
                    import traceback
                    st.error(traceback.format_exc())
    
    # Display Launch Plan
    if has_launch_plan:
        st.markdown("---")
        st.subheader("📋 Your 90-Day Launch Roadmap")
        
        # Convert serialized DataFrame back to DataFrame
        import pandas as pd
        launch_df = pd.DataFrame(state["launch_plan_df"])
        
        # Add date information if available
        if "Start Date" in launch_df.columns and "End Date" in launch_df.columns:
            launch_df["Date Range"] = launch_df.apply(
                lambda row: f"{row['Start Date']} to {row['End Date']}", axis=1
            )
        
        # Display summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_weeks = len(launch_df)
            st.metric("Total Weeks", total_weeks)
        
        with col2:
            phases = launch_df["phase"].nunique() if "phase" in launch_df.columns else 0
            st.metric("Phases", phases)
        
        with col3:
            completed = len(launch_df[launch_df["status"] == "Completed"]) if "status" in launch_df.columns else 0
            st.metric("Completed", completed)
        
        with col4:
            pending = len(launch_df[launch_df["status"] == "Pending"]) if "status" in launch_df.columns else total_weeks
            st.metric("Pending", pending)
        
        st.markdown("---")
        
        # Display plan in tabs
        tab1, tab2, tab3 = st.tabs(["📊 Timeline View", "📝 Detailed Tasks", "📥 Export"])
        
        with tab1:
            st.markdown("### Timeline by Phase")
            
            # Group by phase
            if "phase" in launch_df.columns:
                phases = launch_df["phase"].unique()
                
                for phase in phases:
                    phase_df = launch_df[launch_df["phase"] == phase]
                    
                    with st.expander(f"🎯 {phase} (Weeks {phase_df['week'].min()}-{phase_df['week'].max()})", expanded=True):
                        for _, row in phase_df.iterrows():
                            week_col, deliverable_col, owner_col, status_col = st.columns([1, 5, 2, 2])
                            
                            with week_col:
                                st.markdown(f"**Week {row['week']}**")
                            
                            with deliverable_col:
                                st.markdown(row['deliverables'])
                            
                            with owner_col:
                                st.markdown(f"👤 {row['owner']}")
                            
                            with status_col:
                                status = row.get('status', 'Pending')
                                if status == "Completed":
                                    st.markdown("✅ Done")
                                elif status == "In Progress":
                                    st.markdown("🔄 Active")
                                else:
                                    st.markdown("⏳ Pending")
            else:
                st.dataframe(launch_df, use_container_width=True)
        
        with tab2:
            st.markdown("### Detailed Task List")
            st.caption("Full breakdown of deliverables, owners, and status")
            
            # Display as interactive dataframe
            st.dataframe(
                launch_df,
                use_container_width=True,
                height=600
            )
            
            # Option to edit status (simple version)
            st.markdown("---")
            st.markdown("**💡 Tip:** Export to CSV to track progress in your project management tool")
        
        with tab3:
            st.markdown("### Export Options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📥 Download as CSV")
                st.caption("Import into Excel, Google Sheets, or project management tools")
                
                csv_data = launch_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"{state['company_name']}_launch_plan.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                st.markdown("#### 📋 Copy to Clipboard")
                st.caption("Copy as markdown for documentation")
                
                # Generate markdown table
                markdown_table = launch_df.to_markdown(index=False)
                st.text_area(
                    "Markdown Format",
                    value=markdown_table,
                    height=200,
                    label_visibility="collapsed"
                )
            
            st.markdown("---")
            st.markdown("#### 🔗 Integration Tips")
            st.markdown("""
            - **Asana/Trello**: Import CSV and map columns to custom fields
            - **Notion**: Paste markdown table into a Notion page
            - **Monday.com**: Use CSV import to create new board
            - **ClickUp**: Import tasks via CSV with custom fields mapping
            """)
    
    else:
        # No launch plan yet - show placeholder
        st.info("📝 Configure your launch settings above and click 'Generate Plan' to create your customized 90-day roadmap")
        
        st.markdown("### What You'll Get:")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ✅ **Week-by-week task breakdown**
            - Phase-based organization
            - Clear deliverables
            - Owner assignments
            """)
        
        with col2:
            st.markdown("""
            ✅ **Customized for your brand type**
            - SaaS: Product-led growth focus
            - D2C: E-commerce & retail strategy
            - Agency: Service delivery & client acquisition
            - E-commerce: Marketplace & inventory management
            """)
    
    # Navigation
    st.markdown("---")
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
    
    state = st.session_state.brand_state
    executor = st.session_state.workflow_executor
    
    # Check prerequisites
    if not state.get("company_name"):
        st.warning("⚠️ Please complete the Brand Foundations page first.")
        if st.button("Go to Foundations →"):
            st.session_state.current_page = "foundations"
            st.rerun()
        return
    
    # Check if KPI projections exist
    has_kpis = state.get("kpi_projections") is not None
    
    # Configuration Section
    st.subheader("🎯 KPI Configuration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        base_visitors = st.number_input(
            "Weekly Visitors (Week 1)",
            min_value=100,
            max_value=100000,
            value=state.get("base_visitors", 1000),
            step=100,
            help="Expected number of website visitors in the first week"
        )
        if base_visitors != state.get("base_visitors"):
            state["base_visitors"] = base_visitors
            save_state_to_file(state)
    
    with col2:
        conversion_rate = st.number_input(
            "Conversion Rate (%)",
            min_value=0.1,
            max_value=50.0,
            value=state.get("conversion_rate", 2.5),
            step=0.1,
            help="Percentage of visitors who signup/convert"
        )
        if conversion_rate != state.get("conversion_rate"):
            state["conversion_rate"] = conversion_rate
            save_state_to_file(state)
    
    with col3:
        growth_rate = st.number_input(
            "Weekly Growth Rate (%)",
            min_value=0.0,
            max_value=100.0,
            value=state.get("growth_rate", 10.0),
            step=1.0,
            help="Expected week-over-week growth rate"
        )
        if growth_rate != state.get("growth_rate"):
            state["growth_rate"] = growth_rate
            save_state_to_file(state)
    
    # Advanced Settings (Collapsible)
    with st.expander("⚙️ Advanced Settings"):
        col1, col2 = st.columns(2)
        
        with col1:
            lead_conversion = st.slider(
                "Lead Conversion Rate (%)",
                min_value=10.0,
                max_value=100.0,
                value=state.get("lead_conversion", 30.0),
                step=5.0,
                help="Percentage of signups that become qualified leads"
            )
            if lead_conversion != state.get("lead_conversion"):
                state["lead_conversion"] = lead_conversion
                save_state_to_file(state)
        
        with col2:
            revenue_per_lead = st.number_input(
                "Revenue per Lead ($)",
                min_value=10.0,
                max_value=10000.0,
                value=state.get("revenue_per_lead", 500.0),
                step=50.0,
                help="Average revenue expected per qualified lead"
            )
            if revenue_per_lead != state.get("revenue_per_lead"):
                state["revenue_per_lead"] = revenue_per_lead
                save_state_to_file(state)
    
    st.markdown("---")
    
    # Generate KPIs Button
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if not has_kpis:
            st.info("💡 Click the button to generate your 90-day KPI projections")
        else:
            st.success("✅ KPI projections generated! You can regenerate with updated parameters.")
    
    with col2:
        if st.button("🤖 Generate KPIs", type="primary", use_container_width=True):
            with st.spinner("Calculating KPI projections..."):
                try:
                    # Execute the KPI node
                    updated_state = executor.execute_step("kpis", state)
                    
                    # Update session state
                    st.session_state.brand_state = updated_state
                    save_state_to_file(updated_state)
                    st.success("🎉 KPI projections generated successfully!")
                    st.rerun()
                
                except Exception as e:
                    st.error(f"Error generating KPIs: {str(e)}")
    
    # Display KPI Dashboard
    if has_kpis:
        st.markdown("---")
        
        # Tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "📊 Detailed Metrics", "💡 AI Insights", "📥 Export"])
        
        with tab1:
            st.subheader("90-Day Projection Overview")
            
            import pandas as pd
            kpi_df = pd.DataFrame(state["kpi_projections"])
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            total_visitors = kpi_df["Visitors"].sum()
            total_signups = kpi_df["Signups"].sum()
            total_leads = kpi_df["Leads"].sum()
            total_revenue = kpi_df["Revenue"].sum()
            
            with col1:
                st.metric("Total Visitors", f"{total_visitors:,}")
            with col2:
                st.metric("Total Signups", f"{total_signups:,}")
            with col3:
                st.metric("Total Leads", f"{total_leads:,}")
            with col4:
                st.metric("Total Revenue", f"${total_revenue:,.0f}")
            
            st.markdown("---")
            
            # Line Charts
            import plotly.graph_objects as go
            
            # Visitors & Signups Chart
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(
                x=kpi_df["Week"],
                y=kpi_df["Visitors"],
                mode='lines+markers',
                name='Visitors',
                line=dict(color='#1f77b4', width=3)
            ))
            fig1.add_trace(go.Scatter(
                x=kpi_df["Week"],
                y=kpi_df["Signups"],
                mode='lines+markers',
                name='Signups',
                line=dict(color='#ff7f0e', width=3)
            ))
            fig1.update_layout(
                title="Weekly Visitors & Signups",
                xaxis_title="Week",
                yaxis_title="Count",
                hovermode='x unified',
                height=400
            )
            st.plotly_chart(fig1, use_container_width=True)
            
            # Revenue Chart
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=kpi_df["Week"],
                y=kpi_df["Revenue"],
                name='Weekly Revenue',
                marker_color='#2ca02c'
            ))
            
            # Add cumulative line
            cumulative_revenue = kpi_df["Revenue"].cumsum()
            fig2.add_trace(go.Scatter(
                x=kpi_df["Week"],
                y=cumulative_revenue,
                mode='lines+markers',
                name='Cumulative Revenue',
                line=dict(color='#d62728', width=3),
                yaxis='y2'
            ))
            
            fig2.update_layout(
                title="Revenue Projection",
                xaxis_title="Week",
                yaxis_title="Weekly Revenue ($)",
                yaxis2=dict(
                    title="Cumulative Revenue ($)",
                    overlaying='y',
                    side='right'
                ),
                hovermode='x unified',
                height=400
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        with tab2:
            st.subheader("Detailed Weekly Metrics")
            
            # Format the dataframe for display
            display_df = kpi_df.copy()
            display_df["Visitors"] = display_df["Visitors"].apply(lambda x: f"{x:,}")
            display_df["Signups"] = display_df["Signups"].apply(lambda x: f"{x:,}")
            display_df["Leads"] = display_df["Leads"].apply(lambda x: f"{x:,}")
            display_df["Revenue"] = display_df["Revenue"].apply(lambda x: f"${x:,.2f}")
            
            st.dataframe(display_df, use_container_width=True, height=500)
            
            st.markdown("---")
            st.markdown("### Key Assumptions")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                **Traffic & Conversion**
                - Starting Visitors: {base_visitors:,}/week
                - Conversion Rate: {conversion_rate}%
                - Weekly Growth: {growth_rate}%
                """)
            
            with col2:
                st.markdown(f"""
                **Lead Generation & Revenue**
                - Lead Conversion: {state.get('lead_conversion', 30.0)}%
                - Revenue per Lead: ${state.get('revenue_per_lead', 500.0):,.2f}
                - Total Pipeline: ${total_revenue:,.0f}
                """)
        
        with tab3:
            st.subheader("💡 AI-Generated Insights")
            
            if state.get("kpi_insights"):
                st.markdown(state["kpi_insights"])
            else:
                st.info("AI insights will be generated along with your KPI projections")
            
            st.markdown("---")
            st.markdown("### Recommendations")
            
            # Calculate some metrics for recommendations
            avg_weekly_growth = ((kpi_df["Visitors"].iloc[-1] / kpi_df["Visitors"].iloc[0]) ** (1/12) - 1) * 100
            final_conversion = (kpi_df["Signups"].iloc[-1] / kpi_df["Visitors"].iloc[-1]) * 100
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📈 Growth Opportunities**")
                if avg_weekly_growth < 10:
                    st.warning("Consider increasing marketing spend to achieve target growth")
                elif avg_weekly_growth > 20:
                    st.success("Strong growth trajectory - ensure infrastructure can scale")
                else:
                    st.info("Healthy growth rate - maintain current strategy")
            
            with col2:
                st.markdown("**🎯 Conversion Optimization**")
                if final_conversion < 2:
                    st.warning("Focus on optimizing your landing page and value proposition")
                elif final_conversion > 5:
                    st.success("Excellent conversion rate - scale your traffic sources")
                else:
                    st.info("Good conversion rate - continue A/B testing")
        
        with tab4:
            st.subheader("📥 Export Options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Download as CSV")
                st.caption("Import into Excel or Google Sheets")
                
                csv_data = kpi_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"{state['company_name']}_kpi_projections.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                st.markdown("#### Copy as JSON")
                st.caption("For API integration or custom tools")
                
                import json
                json_data = kpi_df.to_dict('records')
                st.download_button(
                    label="Download JSON",
                    data=json.dumps(json_data, indent=2),
                    file_name=f"{state['company_name']}_kpi_projections.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            st.markdown("---")
            st.markdown("#### 📊 Google Sheets Formulas")
            st.caption("Use these formulas to track actual vs projected metrics")
            
            formulas_code = """
            # Week-over-Week Growth
            =(B3-B2)/B2
            
            # Conversion Rate
            =C2/B2
            
            # Cumulative Revenue
            =SUM($E$2:E2)
            
            # Target Achievement
            =ACTUAL_VALUE/PROJECTED_VALUE
            """
            st.code(formulas_code, language="excel")
    
    else:
        # No KPIs yet - show preview
        st.info("📝 Configure your KPI parameters above and click 'Generate KPIs' to see your projections")
        
        st.markdown("### What You'll Get:")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ✅ **Visual Dashboard**
            - Interactive charts with Plotly
            - Visitor & signup trends
            - Revenue projections
            - Week-by-week breakdown
            """)
        
        with col2:
            st.markdown("""
            ✅ **AI-Powered Insights**
            - Growth opportunity analysis
            - Conversion optimization tips
            - Benchmark comparisons
            - Actionable recommendations
            """)
    
    # Navigation
    st.markdown("---")
    
    # Workflow completion celebration (Phase 7 feature)
    if has_kpis and state.get("current_step", 0) >= 5:
        st.balloons()
        st.success("🎉 **Congratulations!** You've completed the entire BrandForge AI workflow!")
        
        with st.expander("📊 Your Accomplishments", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**✅ Brand Strategy**")
                st.caption(f"• Vision: {state.get('vision', 'N/A')[:50]}...")
                st.caption(f"• Mission: {state.get('mission', 'N/A')[:50]}...")
                st.caption(f"• Values: {len(state.get('values', []))} defined")
            
            with col2:
                st.markdown("**✅ Brand Identity**")
                st.caption("• Visual identity created")
                st.caption("• Messaging guide developed")
                st.caption("• Brand assets packaged")
            
            with col3:
                st.markdown("**✅ Launch Plan**")
                if state.get("launch_plan_df"):
                    launch_df_check = pd.DataFrame(state["launch_plan_df"])
                    st.caption(f"• {len(launch_df_check)} week roadmap")
                st.caption(f"• {total_visitors:,} projected visitors")
                st.caption(f"• ${total_revenue:,.0f} revenue target")
            
            st.markdown("---")
            st.markdown("### 🚀 Next Steps:")
            st.markdown("""
            1. **Download your complete playbook** from the sidebar (📥 Download Everything)
            2. **Share with your team** and gather feedback
            3. **Set up tracking** using the Google Sheets formulas
            4. **Execute your launch plan** week by week
            5. **Monitor KPIs** and adjust strategy as needed
            """)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Launch Plan", use_container_width=True, key="back_to_launch"):
            st.session_state.current_page = "launch_plan"
            st.rerun()
    with col2:
        st.markdown("*🎉 You've reached the end of the workflow!*")


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
