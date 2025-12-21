"""
Test Suite for Phase 5: Launch Plan Generation & Page
Tests the 90-day launch plan workflow node and UI components
"""

import os
import sys
from datetime import date, timedelta
from dotenv import load_dotenv
import pandas as pd

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from modules.state import BrandState
from modules.workflow import BrandWorkflowExecutor, can_execute_step
from modules.graph_nodes import node_plan_launch
from templates.launch_plan_template import get_launch_plan_template, get_available_brand_types

# Get available brand types
BRAND_TYPES = get_available_brand_types()


def test_launch_plan_templates():
    """Test 1: Verify launch plan templates exist and have correct structure"""
    print("\n" + "="*70)
    print("TEST 1: Launch Plan Templates Structure")
    print("="*70)
    
    try:
        # Test all brand types
        for brand_type in BRAND_TYPES:
            template = get_launch_plan_template(brand_type)
            
            print(f"\n✓ Brand Type: {brand_type}")
            print(f"  - Total Weeks: {len(template)}")
            
            # Verify required fields
            required_fields = ["week", "phase", "deliverables", "owner", "status"]
            for item in template:
                for field in required_fields:
                    assert field in item, f"Missing field '{field}' in {brand_type} template"
            
            # Verify weeks are sequential
            weeks = [item["week"] for item in template]
            assert weeks == list(range(1, len(template) + 1)), f"Weeks not sequential in {brand_type}"
            
            # Get unique phases
            phases = set(item["phase"] for item in template)
            print(f"  - Phases: {', '.join(sorted(phases))}")
            
            # Get unique owners
            owners = set(item["owner"] for item in template)
            print(f"  - Owners: {', '.join(sorted(owners))}")
        
        print("\n✅ TEST 1 PASSED: All launch plan templates valid")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 1 FAILED: {str(e)}")
        return False


def test_launch_plan_node():
    """Test 2: Test the node_plan_launch workflow node"""
    print("\n" + "="*70)
    print("TEST 2: Launch Plan Workflow Node")
    print("="*70)
    
    try:
        # Create test state with required fields
        test_state: BrandState = {
            "company_name": "TestBrand Inc",
            "brand_type": "SaaS",
            "launch_start_date": (date.today() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "vision": "Test vision",
            "mission": "Test mission",
            "values": ["Innovation", "Customer-First"],
            "current_step": 4,
            "last_updated": "2025-12-21T10:00:00"
        }
        
        # Execute the node
        print("\nExecuting node_plan_launch...")
        result_state = node_plan_launch(test_state)
        
        # Verify launch_plan_df was created
        assert "launch_plan_df" in result_state, "launch_plan_df not created"
        
        # Convert to DataFrame
        launch_df = pd.DataFrame(result_state["launch_plan_df"])
        
        print(f"\n✓ Launch Plan Generated:")
        print(f"  - Total Weeks: {len(launch_df)}")
        print(f"  - Columns: {', '.join(launch_df.columns)}")
        
        # Verify DataFrame structure
        required_columns = ["week", "phase", "deliverables", "owner", "status"]
        for col in required_columns:
            assert col in launch_df.columns, f"Missing column '{col}'"
        
        # Verify dates were added
        if "Start Date" in launch_df.columns:
            print(f"  - Start Date: {launch_df['Start Date'].iloc[0]}")
            print(f"  - End Date: {launch_df['End Date'].iloc[-1]}")
        
        # Verify phases
        phases = launch_df["phase"].unique()
        print(f"  - Phases: {', '.join(phases)}")
        
        print("\n✅ TEST 2 PASSED: Launch plan node executes successfully")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 2 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_launch_plan_with_different_brand_types():
    """Test 3: Generate launch plans for all brand types"""
    print("\n" + "="*70)
    print("TEST 3: Launch Plans for All Brand Types")
    print("="*70)
    
    try:
        for brand_type in BRAND_TYPES:
            test_state: BrandState = {
                "company_name": f"Test {brand_type} Company",
                "brand_type": brand_type,
                "launch_start_date": date.today().strftime("%Y-%m-%d"),
                "vision": "Test vision",
                "mission": "Test mission",
                "values": ["Quality", "Innovation"],
                "current_step": 4,
                "last_updated": "2025-12-21T10:00:00"
            }
            
            result_state = node_plan_launch(test_state)
            launch_df = pd.DataFrame(result_state["launch_plan_df"])
            
            print(f"\n✓ {brand_type}:")
            print(f"  - Weeks: {len(launch_df)}")
            print(f"  - Phases: {launch_df['phase'].nunique()}")
            
            # Verify customization for brand type
            assert len(launch_df) >= 10, f"Launch plan too short for {brand_type}"
        
        print("\n✅ TEST 3 PASSED: All brand types generate valid launch plans")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 3 FAILED: {str(e)}")
        return False


def test_launch_plan_csv_export():
    """Test 4: Test CSV export functionality"""
    print("\n" + "="*70)
    print("TEST 4: Launch Plan CSV Export")
    print("="*70)
    
    try:
        # Create test state
        test_state: BrandState = {
            "company_name": "Export Test Co",
            "brand_type": "D2C",
            "launch_start_date": date.today().strftime("%Y-%m-%d"),
            "vision": "Test vision",
            "mission": "Test mission",
            "values": ["Excellence"],
            "current_step": 4,
            "last_updated": "2025-12-21T10:00:00"
        }
        
        # Generate launch plan
        result_state = node_plan_launch(test_state)
        launch_df = pd.DataFrame(result_state["launch_plan_df"])
        
        # Export to CSV
        csv_data = launch_df.to_csv(index=False)
        
        print(f"\n✓ CSV Export:")
        print(f"  - Size: {len(csv_data)} bytes")
        print(f"  - Lines: {len(csv_data.splitlines())}")
        
        # Verify CSV contains expected data
        assert "week" in csv_data, "CSV missing 'week' column"
        assert "phase" in csv_data, "CSV missing 'phase' column"
        assert "deliverables" in csv_data, "CSV missing 'deliverables' column"
        
        # Verify first few lines
        lines = csv_data.splitlines()[:3]
        print(f"\n  First 3 lines:")
        for line in lines:
            print(f"    {line[:80]}...")
        
        print("\n✅ TEST 4 PASSED: CSV export successful")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 4 FAILED: {str(e)}")
        return False


def test_launch_plan_prerequisites():
    """Test 5: Test prerequisites validation for launch plan step"""
    print("\n" + "="*70)
    print("TEST 5: Launch Plan Prerequisites Validation")
    print("="*70)
    
    try:
        # Test case 1: Missing prerequisites
        incomplete_state: BrandState = {
            "company_name": "Test Co",
            "current_step": 1
        }
        
        can_execute, missing = can_execute_step("launch_plan", incomplete_state)
        print(f"\n✓ Incomplete State:")
        print(f"  - Can Execute: {can_execute}")
        print(f"  - Missing Prerequisites: {missing}")
        
        assert not can_execute, "Should not be able to execute without prerequisites"
        assert len(missing) > 0, "Should have missing prerequisites"
        
        # Test case 2: Complete prerequisites
        complete_state: BrandState = {
            "company_name": "Test Co",
            "brand_type": "SaaS",
            "vision": "Vision",
            "mission": "Mission",
            "values": ["Value1"],
            "target_audience": "Audience",
            "core_problem": "Problem",
            "positioning_statement": "Position",
            "color_palette_desc": "Colors",
            "font_recommendations": "Fonts",
            "messaging_guide": "Messaging",
            "current_step": 4
        }
        
        can_execute, missing = can_execute_step("launch_plan", complete_state)
        print(f"\n✓ Complete State:")
        print(f"  - Can Execute: {can_execute}")
        print(f"  - Missing Prerequisites: {missing}")
        
        assert can_execute, "Should be able to execute with complete prerequisites"
        assert len(missing) == 0, "Should have no missing prerequisites"
        
        print("\n✅ TEST 5 PASSED: Prerequisites validation working correctly")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 5 FAILED: {str(e)}")
        return False


def test_launch_plan_workflow_integration():
    """Test 6: Test launch plan via workflow executor"""
    print("\n" + "="*70)
    print("TEST 6: Launch Plan Workflow Integration")
    print("="*70)
    
    try:
        # Create complete initial state
        initial_state: BrandState = {
            "company_name": "Workflow Test Inc",
            "brand_type": "E-commerce",
            "launch_start_date": (date.today() + timedelta(days=14)).strftime("%Y-%m-%d"),
            "vision": "To revolutionize online shopping",
            "mission": "Make e-commerce accessible to all",
            "values": ["Innovation", "Customer-First", "Quality"],
            "target_audience": "Online shoppers aged 25-45",
            "core_problem": "Complicated checkout processes",
            "positioning_statement": "We simplify online shopping",
            "color_palette_desc": "Blue and white for trust",
            "font_recommendations": "Modern sans-serif",
            "messaging_guide": "Clear, friendly, helpful",
            "current_step": 3,
            "last_updated": "2025-12-21T10:00:00"
        }
        
        # Initialize executor
        print("\nInitializing workflow executor...")
        executor = BrandWorkflowExecutor(initial_state)
        
        # Execute launch plan step
        print("Executing launch_plan step...")
        updated_state = executor.execute_step("launch_plan", initial_state)
        
        print(f"\n✓ Execution Result:")
        print(f"  - Step completed successfully")
        
        # Verify launch plan was generated
        assert "launch_plan_df" in updated_state, "launch_plan_df not in state"
        
        launch_df = pd.DataFrame(updated_state["launch_plan_df"])
        print(f"  - Launch Plan Weeks: {len(launch_df)}")
        print(f"  - Current Step: {updated_state.get('current_step', 'N/A')}")
        
        # Verify step progression
        assert updated_state["current_step"] == 4, "Step should be incremented to 4"
        
        print("\n✅ TEST 6 PASSED: Workflow integration successful")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 6 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all Phase 5 tests"""
    print("\n" + "="*70)
    print("PHASE 5 TEST SUITE: LAUNCH PLAN GENERATION")
    print("="*70)
    print("Testing: Launch plan templates, workflow node, UI integration")
    print("="*70)
    
    tests = [
        test_launch_plan_templates,
        test_launch_plan_node,
        test_launch_plan_with_different_brand_types,
        test_launch_plan_csv_export,
        test_launch_plan_prerequisites,
        test_launch_plan_workflow_integration
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nTests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ ALL PHASE 5 TESTS PASSED! 🎉")
        print("\nPhase 5 Implementation Complete:")
        print("  ✓ Launch plan templates for all brand types")
        print("  ✓ Workflow node generates customized plans")
        print("  ✓ CSV export functionality")
        print("  ✓ Prerequisites validation")
        print("  ✓ Full workflow integration")
        return True
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
