"""
Test Suite for Phase 6: KPI Dashboard & Projections
Tests the KPI calculation workflow node and dashboard components
"""

import os
import sys
from dotenv import load_dotenv
import pandas as pd

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from modules.state import BrandState
from modules.workflow import BrandWorkflowExecutor, can_execute_step
from modules.graph_nodes import node_calculate_kpis
from modules.utils import calculate_kpi_projections


def test_kpi_calculation_utility():
    """Test 1: Verify KPI calculation utility function"""
    print("\n" + "="*70)
    print("TEST 1: KPI Calculation Utility Function")
    print("="*70)
    
    try:
        # Test with standard parameters
        projections = calculate_kpi_projections(
            base_visitors=1000,
            conversion_rate=0.025,  # 2.5%
            growth_rate=0.10,  # 10%
            weeks=13,
            lead_conversion=0.30,  # 30%
            revenue_per_lead=500.0
        )
        
        print(f"\n✓ Projections Generated:")
        print(f"  - Weeks: {len(projections)}")
        print(f"  - Columns: {', '.join(projections.columns)}")
        
        # Verify DataFrame structure
        required_columns = ["Week", "Visitors", "Signups", "Leads", "Revenue"]
        for col in required_columns:
            assert col in projections.columns, f"Missing column '{col}'"
        
        # Verify data types
        assert len(projections) == 13, "Should have 13 weeks"
        assert projections["Visitors"].dtype in [int, 'int64'], "Visitors should be integer"
        assert projections["Revenue"].dtype in [float, 'float64'], "Revenue should be float"
        
        # Verify growth
        week1_visitors = projections["Visitors"].iloc[0]
        week13_visitors = projections["Visitors"].iloc[-1]
        print(f"  - Week 1 Visitors: {week1_visitors:,}")
        print(f"  - Week 13 Visitors: {week13_visitors:,}")
        print(f"  - Growth Factor: {week13_visitors / week1_visitors:.2f}x")
        
        # Verify calculations
        total_revenue = projections["Revenue"].sum()
        print(f"  - Total Revenue: ${total_revenue:,.2f}")
        
        assert week13_visitors > week1_visitors, "Visitors should grow over time"
        
        print("\n✅ TEST 1 PASSED: KPI calculations working correctly")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 1 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_kpi_node():
    """Test 2: Test the node_calculate_kpis workflow node"""
    print("\n" + "="*70)
    print("TEST 2: KPI Calculation Workflow Node")
    print("="*70)
    
    try:
        # Create test state with required fields
        test_state: BrandState = {
            "company_name": "TestBrand Inc",
            "brand_type": "SaaS",
            "base_visitors": 1500,
            "conversion_rate": 3.0,
            "growth_rate": 12.0,
            "lead_conversion": 35.0,
            "revenue_per_lead": 600.0,
            "vision": "Test vision",
            "mission": "Test mission",
            "values": ["Innovation"],
            "current_step": 4,
            "last_updated": "2025-12-21T10:00:00"
        }
        
        # Execute the node
        print("\nExecuting node_calculate_kpis...")
        result_state = node_calculate_kpis(test_state)
        
        # Verify kpi_projections was created
        assert "kpi_projections" in result_state, "kpi_projections not created"
        
        # Convert to DataFrame
        kpi_list = result_state["kpi_projections"]
        kpi_df = pd.DataFrame(kpi_list)
        
        print(f"\n✓ KPI Projections Generated:")
        print(f"  - Total Weeks: {len(kpi_df)}")
        print(f"  - Columns: {', '.join(kpi_df.columns)}")
        
        # Verify KPI insights
        assert "kpi_insights" in result_state, "kpi_insights not created"
        insights = result_state["kpi_insights"]
        print(f"  - Insights Length: {len(insights)} chars")
        
        # Verify step progression
        assert result_state["current_step"] == 5, "Step should be incremented to 5"
        
        # Verify totals
        total_visitors = kpi_df["Visitors"].sum()
        total_revenue = kpi_df["Revenue"].sum()
        print(f"  - Total Visitors: {total_visitors:,}")
        print(f"  - Total Revenue: ${total_revenue:,.2f}")
        
        print("\n✅ TEST 2 PASSED: KPI node executes successfully")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 2 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_kpi_with_different_parameters():
    """Test 3: Generate KPIs with different parameter sets"""
    print("\n" + "="*70)
    print("TEST 3: KPI Generation with Different Parameters")
    print("="*70)
    
    try:
        test_cases = [
            {"base": 500, "conv": 2.0, "growth": 5.0, "name": "Conservative"},
            {"base": 2000, "conv": 4.0, "growth": 15.0, "name": "Aggressive"},
            {"base": 1000, "conv": 2.5, "growth": 10.0, "name": "Moderate"},
        ]
        
        for case in test_cases:
            test_state: BrandState = {
                "company_name": f"{case['name']} Brand",
                "brand_type": "SaaS",
                "base_visitors": case["base"],
                "conversion_rate": case["conv"],
                "growth_rate": case["growth"],
                "lead_conversion": 30.0,
                "revenue_per_lead": 500.0,
                "vision": "Test",
                "mission": "Test",
                "values": ["Test"],
                "current_step": 4,
                "last_updated": "2025-12-21T10:00:00"
            }
            
            result_state = node_calculate_kpis(test_state)
            kpi_df = pd.DataFrame(result_state["kpi_projections"])
            
            total_visitors = kpi_df["Visitors"].sum()
            total_revenue = kpi_df["Revenue"].sum()
            
            print(f"\n✓ {case['name']} Scenario:")
            print(f"  - Base: {case['base']}, Conv: {case['conv']}%, Growth: {case['growth']}%")
            print(f"  - Total Visitors: {total_visitors:,}")
            print(f"  - Total Revenue: ${total_revenue:,.0f}")
            
            assert len(kpi_df) == 13, "Should have 13 weeks"
            assert total_revenue > 0, "Should generate revenue"
        
        print("\n✅ TEST 3 PASSED: All parameter sets generate valid KPIs")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 3 FAILED: {str(e)}")
        return False


def test_kpi_export_formats():
    """Test 4: Test CSV and JSON export functionality"""
    print("\n" + "="*70)
    print("TEST 4: KPI Export Formats")
    print("="*70)
    
    try:
        # Generate test projections
        projections = calculate_kpi_projections(
            base_visitors=1000,
            conversion_rate=0.025,
            growth_rate=0.10,
            weeks=13,
            lead_conversion=0.30,
            revenue_per_lead=500.0
        )
        
        # Test CSV export
        csv_data = projections.to_csv(index=False)
        print(f"\n✓ CSV Export:")
        print(f"  - Size: {len(csv_data)} bytes")
        print(f"  - Lines: {len(csv_data.splitlines())}")
        
        assert "Week" in csv_data, "CSV missing Week column"
        assert "Revenue" in csv_data, "CSV missing Revenue column"
        
        # Test JSON export
        import json
        json_data = projections.to_dict('records')
        json_str = json.dumps(json_data, indent=2)
        print(f"\n✓ JSON Export:")
        print(f"  - Size: {len(json_str)} bytes")
        print(f"  - Records: {len(json_data)}")
        
        assert len(json_data) == 13, "Should have 13 records"
        assert "Week" in json_data[0], "JSON missing Week field"
        
        # Verify first record
        first_record = json_data[0]
        print(f"\n  Sample Record:")
        print(f"    Week: {first_record['Week']}")
        print(f"    Visitors: {first_record['Visitors']}")
        print(f"    Revenue: ${first_record['Revenue']:,.2f}")
        
        print("\n✅ TEST 4 PASSED: Export formats working correctly")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 4 FAILED: {str(e)}")
        return False


def test_kpi_prerequisites():
    """Test 5: Test prerequisites validation for KPI step"""
    print("\n" + "="*70)
    print("TEST 5: KPI Prerequisites Validation")
    print("="*70)
    
    try:
        # Test case 1: Missing prerequisites
        incomplete_state: BrandState = {
            "company_name": "Test Co",
            "current_step": 1
        }
        
        can_execute, missing = can_execute_step("kpis", incomplete_state)
        print(f"\n✓ Incomplete State:")
        print(f"  - Can Execute: {can_execute}")
        print(f"  - Missing Prerequisites: {missing}")
        
        # Should have some missing prerequisites
        assert not can_execute or missing, "Should not be able to execute or should show missing prerequisites"
        
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
            "launch_plan_df": {},
            "base_visitors": 1000,
            "conversion_rate": 2.5,
            "growth_rate": 10.0,
            "current_step": 4
        }
        
        can_execute, missing = can_execute_step("kpis", complete_state)
        print(f"\n✓ Complete State:")
        print(f"  - Can Execute: {can_execute}")
        print(f"  - Missing Prerequisites: {missing}")
        
        print("\n✅ TEST 5 PASSED: Prerequisites validation working")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 5 FAILED: {str(e)}")
        return False


def test_kpi_workflow_integration():
    """Test 6: Test KPI generation via workflow executor"""
    print("\n" + "="*70)
    print("TEST 6: KPI Workflow Integration")
    print("="*70)
    
    try:
        # Create complete initial state
        initial_state: BrandState = {
            "company_name": "Workflow Test Inc",
            "brand_type": "D2C",
            "base_visitors": 2000,
            "conversion_rate": 3.5,
            "growth_rate": 15.0,
            "lead_conversion": 40.0,
            "revenue_per_lead": 750.0,
            "vision": "To revolutionize e-commerce",
            "mission": "Make online shopping easy",
            "values": ["Innovation", "Customer-First"],
            "target_audience": "Online shoppers",
            "core_problem": "Complex checkout",
            "positioning_statement": "We simplify shopping",
            "color_palette_desc": "Blue and white",
            "font_recommendations": "Modern sans-serif",
            "messaging_guide": "Clear and friendly",
            "launch_plan_df": {"week": [1, 2, 3]},
            "current_step": 4,
            "last_updated": "2025-12-21T10:00:00"
        }
        
        # Initialize executor
        print("\nInitializing workflow executor...")
        executor = BrandWorkflowExecutor(initial_state)
        
        # Execute KPI step
        print("Executing kpis step...")
        updated_state = executor.execute_step("kpis", initial_state)
        
        print(f"\n✓ Execution Result:")
        print(f"  - Step completed successfully")
        
        # Verify KPIs were generated
        assert "kpi_projections" in updated_state, "kpi_projections not in state"
        assert "kpi_insights" in updated_state, "kpi_insights not in state"
        
        kpi_df = pd.DataFrame(updated_state["kpi_projections"])
        print(f"  - KPI Weeks: {len(kpi_df)}")
        print(f"  - Insights Length: {len(updated_state['kpi_insights'])} chars")
        print(f"  - Current Step: {updated_state.get('current_step', 'N/A')}")
        
        # Verify step progression
        assert updated_state["current_step"] == 5, "Step should be incremented to 5"
        
        # Verify metrics
        total_visitors = kpi_df["Visitors"].sum()
        total_revenue = kpi_df["Revenue"].sum()
        print(f"  - Total Visitors: {total_visitors:,}")
        print(f"  - Total Revenue: ${total_revenue:,.0f}")
        
        assert total_visitors > 0, "Should have visitors"
        assert total_revenue > 0, "Should have revenue"
        
        print("\n✅ TEST 6 PASSED: Workflow integration successful")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 6 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all Phase 6 tests"""
    print("\n" + "="*70)
    print("PHASE 6 TEST SUITE: KPI DASHBOARD & PROJECTIONS")
    print("="*70)
    print("Testing: KPI calculations, workflow node, dashboard integration")
    print("="*70)
    
    tests = [
        test_kpi_calculation_utility,
        test_kpi_node,
        test_kpi_with_different_parameters,
        test_kpi_export_formats,
        test_kpi_prerequisites,
        test_kpi_workflow_integration
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
        print("\n✅ ALL PHASE 6 TESTS PASSED! 🎉")
        print("\nPhase 6 Implementation Complete:")
        print("  ✓ KPI calculation utility function")
        print("  ✓ Workflow node generates projections")
        print("  ✓ Multiple parameter scenarios")
        print("  ✓ CSV/JSON export functionality")
        print("  ✓ Prerequisites validation")
        print("  ✓ Full workflow integration")
        return True
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
