"""
Test Phase 4: Brand Identity Page Implementation
Tests the complete identity generation and asset creation functionality
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add modules to path
sys.path.append(str(Path(__file__).parent))

from modules.state import create_empty_state
from modules.workflow import BrandWorkflowExecutor, can_execute_step
from modules.utils import generate_playbook_markdown, create_brand_playbook_zip
from modules.langchain_agents import generate_brand_identity

# Load environment variables
load_dotenv()


def print_section(title: str):
    """Print formatted section header."""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80 + "\n")


def test_identity_generation():
    """Test 1: Brand Identity Generation"""
    print_section("TEST 1: Brand Identity Generation")
    
    try:
        # Create state with foundations
        state = create_empty_state()
        state["company_name"] = "TechFlow AI"
        state["target_audience"] = "Software developers building AI applications"
        state["brand_voice"] = "Professional"
        state["vision"] = "Empower developers to build AI apps effortlessly"
        state["mission"] = "Simplify AI infrastructure for rapid development"
        state["values"] = ["Innovation", "Simplicity", "Developer-First", "Reliability", "Speed"]
        state["positioning_statement"] = "For developers who need fast AI deployment"
        
        print("📝 Test state prepared with foundations")
        print(f"   Brand Voice: {state['brand_voice']}")
        print(f"   Values: {len(state['values'])} core values")
        
        # Generate identity via direct function call
        print("\n🎨 Generating brand identity...")
        identity = generate_brand_identity(
            company_name=state["company_name"],
            brand_voice=state["brand_voice"],
            values=state["values"],
            target_audience=state["target_audience"],
            positioning=state["positioning_statement"]
        )
        
        # Check results
        if (identity.get("color_palette_desc") and 
            identity.get("font_recommendations") and 
            identity.get("messaging_guide")):
            
            print("\n✅ Identity generated successfully!")
            print(f"\n📊 Generated Components:")
            print(f"   Color Palette: {len(identity['color_palette_desc'])} chars")
            print(f"   Font Recommendations: {len(identity['font_recommendations'])} chars")
            print(f"   Messaging Guide: {len(identity['messaging_guide'])} chars")
            
            # Show sample
            color_sample = identity['color_palette_desc'][:150] if len(identity['color_palette_desc']) > 150 else identity['color_palette_desc']
            print(f"\n📋 Sample Color Palette:")
            print(f"   {color_sample}...")
            
            return True
        else:
            print("❌ Identity generation incomplete - missing components")
            return False
    
    except Exception as e:
        print(f"❌ Identity generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_identity_workflow_node():
    """Test 2: Identity Node via Workflow"""
    print_section("TEST 2: Identity Node Execution via Workflow")
    
    try:
        # Create executor
        executor = BrandWorkflowExecutor(use_flexible=False)
        
        # Prepare state
        state = create_empty_state()
        state["company_name"] = "BrandForge AI"
        state["target_audience"] = "Startup founders building consumer brands"
        state["brand_voice"] = "Friendly"
        state["vision"] = "Make brand building accessible to all founders"
        state["mission"] = "Provide structured guidance for brand development"
        state["values"] = ["Accessibility", "Structure", "Guidance", "Innovation", "Empowerment"]
        state["positioning_statement"] = "For founders who need brand development help"
        
        print("📝 State prepared for workflow execution")
        
        # Check prerequisites
        can_exec, message = can_execute_step("identity", state)
        print(f"\n✓ Prerequisites check: {can_exec}")
        
        if not can_exec:
            print(f"   Message: {message}")
            return False
        
        # Execute identity node
        print("\n🔄 Executing identity node via workflow...")
        updated_state = executor.execute_step("identity", state)
        
        # Verify results
        if (updated_state.get("color_palette_desc") and 
            updated_state.get("font_recommendations") and 
            updated_state.get("messaging_guide")):
            
            print("\n✅ Workflow identity node executed successfully!")
            print(f"   Current Step: {updated_state.get('current_step', 0)}")
            print(f"   Last Updated: {updated_state.get('last_updated', 'N/A')[:19]}")
            return True
        else:
            print("❌ Workflow execution did not generate complete identity")
            return False
    
    except Exception as e:
        print(f"❌ Workflow execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_brand_guide_generation():
    """Test 3: Brand Guide Markdown Generation"""
    print_section("TEST 3: Brand Guide Generation")
    
    try:
        # Create complete state
        state = create_empty_state()
        state["company_name"] = "TestCo"
        state["vision"] = "Test vision statement"
        state["mission"] = "Test mission statement"
        state["values"] = ["Value 1", "Value 2", "Value 3"]
        state["target_audience"] = "Test audience"
        state["brand_voice"] = "Professional"
        state["positioning_statement"] = "Test positioning"
        state["color_palette_desc"] = "Primary: Blue (#0066CC) - Trust and professionalism"
        state["font_recommendations"] = "Primary: Inter, Secondary: Merriweather"
        state["messaging_guide"] = "Professional, clear, and concise communication"
        
        print("📝 Generating brand guide markdown...")
        
        markdown = generate_playbook_markdown(state)
        
        if markdown and len(markdown) > 100:
            print(f"\n✅ Brand guide generated!")
            print(f"   Length: {len(markdown)} characters")
            print(f"   Lines: {markdown.count(chr(10))} lines")
            
            # Check for required sections
            required_sections = [
                "Brand Playbook",
                "## Vision",
                "## Mission",
                "## Values",
                "## Brand Identity",
                "## Messaging"
            ]
            
            missing = [s for s in required_sections if s not in markdown]
            
            if missing:
                print(f"\n⚠️ Missing sections: {', '.join(missing)}")
                return False
            else:
                print("\n✅ All required sections present")
                return True
        else:
            print("❌ Brand guide generation failed or too short")
            return False
    
    except Exception as e:
        print(f"❌ Brand guide generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_asset_package_creation():
    """Test 4: Complete Asset Package ZIP"""
    print_section("TEST 4: Asset Package ZIP Creation")
    
    try:
        # Create complete state
        state = create_empty_state()
        state["company_name"] = "TestBrand"
        state["vision"] = "Test vision"
        state["mission"] = "Test mission"
        state["values"] = ["Innovation", "Quality"]
        state["target_audience"] = "Test audience"
        state["brand_voice"] = "Professional"
        state["color_palette_desc"] = "Blue and white"
        state["font_recommendations"] = "Inter font"
        state["messaging_guide"] = "Clear messaging"
        
        print("📦 Creating asset package ZIP...")
        
        zip_buffer = create_brand_playbook_zip(state)
        
        # Check buffer position to verify content was written
        current_pos = zip_buffer.tell()
        buffer_size = len(zip_buffer.getvalue())
        
        if buffer_size > 0:
            size_kb = buffer_size / 1024
            print(f"\n✅ ZIP package created!")
            print(f"   Size: {size_kb:.2f} KB")
            print(f"   Buffer size: {buffer_size} bytes")
            return True
        else:
            print("❌ ZIP package creation failed or empty")
            print(f"   Buffer size: {buffer_size}")
            return False
    
    except Exception as e:
        print(f"❌ Asset package creation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_identity_prerequisites():
    """Test 5: Identity Prerequisites Validation"""
    print_section("TEST 5: Identity Prerequisites Validation")
    
    try:
        # Test with incomplete state
        incomplete_state = create_empty_state()
        incomplete_state["company_name"] = "Test"
        
        can_exec_1, msg_1 = can_execute_step("identity", incomplete_state)
        
        print("📋 Testing incomplete state:")
        print(f"   Can execute: {can_exec_1}")
        print(f"   Message: {msg_1}")
        
        if not can_exec_1:
            print("   ✅ Correctly blocked incomplete state")
        else:
            print("   ❌ Should have blocked incomplete state")
            return False
        
        # Test with complete foundations
        complete_state = create_empty_state()
        complete_state["company_name"] = "Test"
        complete_state["vision"] = "Test vision"
        complete_state["mission"] = "Test mission"
        complete_state["values"] = ["Value 1"]
        complete_state["brand_voice"] = "Professional"
        complete_state["target_audience"] = "Test audience"
        
        can_exec_2, msg_2 = can_execute_step("identity", complete_state)
        
        print("\n📋 Testing complete state:")
        print(f"   Can execute: {can_exec_2}")
        
        if can_exec_2:
            print("   ✅ Correctly allowed complete state")
            return True
        else:
            print(f"   ❌ Should have allowed: {msg_2}")
            return False
    
    except Exception as e:
        print(f"❌ Prerequisites validation failed: {str(e)}")
        return False


def run_all_tests():
    """Run all Phase 4 tests."""
    print("\n" + "=" * 80)
    print("🧪 BRANDFORGE AI - PHASE 4 TEST SUITE")
    print("=" * 80)
    
    tests = [
        ("Identity Generation", test_identity_generation),
        ("Identity Workflow Node", test_identity_workflow_node),
        ("Brand Guide Generation", test_brand_guide_generation),
        ("Asset Package Creation", test_asset_package_creation),
        ("Prerequisites Validation", test_identity_prerequisites)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ Test crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print_section("📊 TEST SUMMARY")
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:.<50} {status}")
    
    print("=" * 80)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    print(f"Total: {passed_count}/{total_count} tests passed ({passed_count/total_count*100:.0f}%)")
    
    if passed_count == total_count:
        print("\n🎉 All tests passed! Phase 4 is fully functional.")
    else:
        print(f"\n⚠️ {total_count - passed_count} test(s) failed. Review errors above.")


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️ WARNING: GOOGLE_API_KEY not found in environment")
        print("Some tests may fail without a valid API key\n")
    
    run_all_tests()
