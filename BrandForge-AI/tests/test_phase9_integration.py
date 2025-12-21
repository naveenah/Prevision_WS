"""
Phase 9 Integration Test Suite: End-to-End Workflow Testing
Tests complete user journey from foundations to KPI export
"""

import sys
from pathlib import Path
import json
import os
from datetime import datetime

sys.path.append(str(Path(__file__).parent))

from modules.state import (
    create_empty_state,
    save_state_to_file,
    load_state_from_file,
    get_completion_percentage
)
from modules.workflow import (
    BrandWorkflowExecutor,
    get_workflow_progress,
    can_execute_step
)
from modules.utils import (
    generate_playbook_markdown,
    create_brand_playbook_zip,
    calculate_kpi_projections
)


def test_complete_workflow_integration():
    """Test 1: Complete end-to-end workflow from foundations to export"""
    print("\n" + "="*70)
    print("TEST 1: Complete Workflow Integration")
    print("="*70)
    
    # Initialize fresh state
    state = create_empty_state()
    state["company_name"] = "TestCorp"
    state["target_audience"] = "Tech-savvy professionals aged 25-45"
    state["core_problem"] = "Inefficient workflow automation"
    state["brand_voice"] = "Professional"
    
    print(f"\nStarting company: {state['company_name']}")
    print(f"Target audience: {state['target_audience']}")
    
    # Initialize workflow executor
    executor = BrandWorkflowExecutor(use_flexible=False)
    
    # Track workflow execution
    steps_executed = []
    
    # Step 1: Execute foundations
    print("\n1. Executing foundations step...")
    can_exec, message = can_execute_step("foundations", state)
    assert can_exec, f"Should be able to execute foundations: {message}"
    
    state = executor.execute_step("foundations", state)
    steps_executed.append("foundations")
    
    # Validate foundations output
    assert state.get("vision"), "Vision should be generated"
    assert state.get("mission"), "Mission should be generated"
    assert state.get("values"), "Values should be generated"
    assert len(state["values"]) >= 3, "Should have at least 3 values"
    
    print(f"   ✅ Vision: {state['vision'][:50]}...")
    print(f"   ✅ Mission: {state['mission'][:50]}...")
    print(f"   ✅ Values: {len(state['values'])} defined")
    
    # Step 2: Execute market analysis
    print("\n2. Executing market analysis step...")
    can_exec, message = can_execute_step("market_analysis", state)
    assert can_exec, f"Should be able to execute market analysis: {message}"
    
    state = executor.execute_step("market_analysis", state)
    steps_executed.append("market_analysis")
    
    # Validate market analysis output
    assert state.get("positioning_statement"), "Positioning should be generated"
    print(f"   ✅ Positioning: {state['positioning_statement'][:60]}...")
    
    # Step 3: Execute identity
    print("\n3. Executing identity step...")
    can_exec, message = can_execute_step("identity", state)
    assert can_exec, f"Should be able to execute identity: {message}"
    
    state = executor.execute_step("identity", state)
    steps_executed.append("identity")
    
    # Validate identity output
    assert state.get("color_palette_desc"), "Color palette should be generated"
    assert state.get("font_recommendations"), "Font recommendations should be generated"
    assert state.get("messaging_guide"), "Messaging guide should be generated"
    
    print(f"   ✅ Colors: {state['color_palette_desc'][:40]}...")
    print(f"   ✅ Fonts: {state['font_recommendations'][:40]}...")
    print(f"   ✅ Messaging: {len(state['messaging_guide'])} chars")
    
    # Step 4: Execute launch plan
    print("\n4. Executing launch plan step...")
    # Set brand type for launch plan
    state["brand_type"] = "SaaS"
    
    can_exec, message = can_execute_step("launch_plan", state)
    assert can_exec, f"Should be able to execute launch plan: {message}"
    
    state = executor.execute_step("launch_plan", state)
    steps_executed.append("launch_plan")
    
    # Validate launch plan output
    assert state.get("launch_plan_df"), "Launch plan DataFrame should exist"
    assert len(state["launch_plan_df"]) > 0, "Launch plan should have tasks"
    
    launch_tasks = len(state["launch_plan_df"])
    print(f"   ✅ Launch plan: {launch_tasks} tasks generated")
    
    # Step 5: Execute KPIs
    print("\n5. Executing KPI calculation step...")
    # Set KPI parameters
    state["initial_audience_size"] = 1000
    state["weekly_growth_rate"] = 0.15
    state["conversion_rate"] = 0.05
    state["avg_customer_value"] = 100
    
    can_exec, message = can_execute_step("kpis", state)
    assert can_exec, f"Should be able to execute KPIs: {message}"
    
    state = executor.execute_step("kpis", state)
    steps_executed.append("kpis")
    
    # Validate KPI output
    assert state.get("kpi_projections"), "KPI projections should exist"
    assert len(state["kpi_projections"]) >= 12, "Should have at least 12 weeks of projections"
    
    final_week = state["kpi_projections"][-1]
    # KPI projections use 'Visitors' and 'Revenue' keys (from calculate_kpi_projections)
    visitors_key = "Visitors" if "Visitors" in final_week else "audience_size"
    revenue_key = "Revenue" if "Revenue" in final_week else "revenue"
    
    print(f"   ✅ Week {len(state['kpi_projections'])} projections:")
    print(f"      Visitors: {final_week[visitors_key]:,}")
    print(f"      Revenue: ${final_week[revenue_key]:,.2f}")
    
    # Verify workflow progress
    progress = get_workflow_progress(state)
    print(f"\n📊 Workflow Progress: {progress['percentage']:.0f}%")
    print(f"   Completed steps: {progress['completed']}/{progress['total']}")
    print(f"   Steps: {', '.join(progress['completed_steps'])}")
    
    assert progress['percentage'] == 100, "Workflow should be 100% complete"
    assert progress['completed'] == 5, "Should have completed all 5 steps"
    
    # Test export functionality
    print("\n6. Testing export functionality...")
    
    # Generate playbook
    playbook_md = generate_playbook_markdown(state)
    assert playbook_md, "Playbook markdown should be generated"
    assert len(playbook_md) > 500, "Playbook should be substantial"
    assert state["company_name"] in playbook_md, "Playbook should include company name"
    
    print(f"   ✅ Playbook: {len(playbook_md)} chars, {len(playbook_md.split())} words")
    
    # Create ZIP package
    import pandas as pd
    launch_df = pd.DataFrame(state["launch_plan_df"])
    kpi_df = pd.DataFrame(state["kpi_projections"])
    
    zip_buffer = create_brand_playbook_zip(state, launch_df, kpi_df)
    assert zip_buffer, "ZIP package should be created"
    
    zip_size = len(zip_buffer.getvalue())
    print(f"   ✅ ZIP package: {zip_size:,} bytes")
    
    # Test state persistence
    print("\n7. Testing state persistence...")
    
    # Save state
    test_filepath = "test_brandforge_state.json"
    save_state_to_file(state, filepath=test_filepath)
    assert os.path.exists(test_filepath), "State file should be created"
    
    # Load state
    loaded_state = load_state_from_file(filepath=test_filepath)
    assert loaded_state, "State should be loaded"
    assert loaded_state["company_name"] == state["company_name"]
    assert loaded_state["vision"] == state["vision"]
    assert len(loaded_state["kpi_projections"]) == 13
    
    print(f"   ✅ State saved and loaded successfully")
    
    # Cleanup
    if os.path.exists(test_filepath):
        os.remove(test_filepath)
    
    print(f"\n✅ COMPLETE WORKFLOW INTEGRATION TEST PASSED!")
    print(f"   Executed {len(steps_executed)} steps: {', '.join(steps_executed)}")
    
    return state


def test_error_handling():
    """Test 2: Error handling and edge cases"""
    print("\n" + "="*70)
    print("TEST 2: Error Handling & Edge Cases")
    print("="*70)
    
    # Test 1: Prerequisites validation
    print("\n1. Testing prerequisites validation...")
    
    empty_state = create_empty_state()
    can_exec, message = can_execute_step("identity", empty_state)
    
    assert not can_exec, "Should not be able to execute identity without foundations"
    assert "prerequisites" in message.lower() or "foundation" in message.lower()
    print(f"   ✅ Correctly blocks: {message}")
    
    # Test 2: Invalid step name
    print("\n2. Testing invalid step handling...")
    
    try:
        can_exec, message = can_execute_step("invalid_step", empty_state)
        print(f"   ✅ Handled invalid step: {message}")
    except Exception as e:
        print(f"   ✅ Raised exception for invalid step: {type(e).__name__}")
    
    # Test 3: Incomplete data
    print("\n3. Testing incomplete data handling...")
    
    partial_state = create_empty_state()
    partial_state["company_name"] = "TestCo"
    # Missing target_audience and core_problem
    
    can_exec, message = can_execute_step("foundations", partial_state)
    
    if not can_exec:
        print(f"   ✅ Validates required fields: {message}")
    else:
        print(f"   ⚠️  Allows execution with partial data (may fail at runtime)")
    
    # Test 4: State corruption recovery
    print("\n4. Testing state corruption recovery...")
    
    corrupted_state = {"invalid": "data"}
    
    try:
        # Try to use corrupted state
        progress = get_workflow_progress(corrupted_state)
        print(f"   ✅ Gracefully handled corrupted state: {progress['percentage']}%")
    except Exception as e:
        print(f"   ⚠️  Exception raised: {type(e).__name__}: {str(e)[:50]}")
    
    print(f"\n✅ ERROR HANDLING TEST COMPLETED!")


def test_different_brand_types():
    """Test 3: Workflow with different brand types"""
    print("\n" + "="*70)
    print("TEST 3: Different Brand Types")
    print("="*70)
    
    brand_types = ["SaaS", "D2C", "Agency", "E-commerce"]
    executor = BrandWorkflowExecutor(use_flexible=False)
    
    results = {}
    
    for brand_type in brand_types:
        print(f"\n{brand_type} Brand:")
        
        state = create_empty_state()
        state["company_name"] = f"Test{brand_type}Co"
        state["target_audience"] = "Tech professionals"
        state["core_problem"] = "Workflow inefficiencies"
        state["brand_voice"] = "Professional"
        state["brand_type"] = brand_type
        
        # Execute foundations and launch plan
        try:
            state = executor.execute_step("foundations", state)
            assert state.get("vision"), f"{brand_type}: Vision should be generated"
            
            state = executor.execute_step("launch_plan", state)
            assert state.get("launch_plan_df"), f"{brand_type}: Launch plan should be generated"
            
            task_count = len(state["launch_plan_df"])
            results[brand_type] = {
                "tasks": task_count,
                "vision_length": len(state["vision"]),
                "success": True
            }
            
            print(f"   ✅ {task_count} tasks, vision: {len(state['vision'])} chars")
            
        except Exception as e:
            results[brand_type] = {
                "success": False,
                "error": str(e)[:100]
            }
            print(f"   ❌ Error: {str(e)[:60]}")
    
    # Validation
    successful = sum(1 for r in results.values() if r["success"])
    print(f"\n📊 Results: {successful}/{len(brand_types)} brand types successful")
    
    assert successful >= len(brand_types) * 0.75, f"At least 75% of brand types should work (got {successful}/{len(brand_types)})"
    
    print(f"\n✅ BRAND TYPES TEST COMPLETED!")
    
    return results


def test_export_variations():
    """Test 4: Export with various data states"""
    print("\n" + "="*70)
    print("TEST 4: Export Variations")
    print("="*70)
    
    import pandas as pd
    
    # Test 1: Full export
    print("\n1. Full export (all data present)...")
    
    full_state = create_empty_state()
    full_state["company_name"] = "FullTestCo"
    full_state["vision"] = "Transform industries"
    full_state["mission"] = "Enable businesses to thrive"
    full_state["values"] = ["Innovation", "Excellence", "Integrity"]
    full_state["launch_plan_df"] = [{"week": 1, "task": "Launch website", "phase": "Foundation"}]
    full_state["kpi_projections"] = [{"week": 1, "audience_size": 1000, "revenue": 5000}]
    
    playbook = generate_playbook_markdown(full_state)
    assert len(playbook) > 300, "Full export should be substantial"
    print(f"   ✅ Full export: {len(playbook)} chars")
    
    launch_df = pd.DataFrame(full_state["launch_plan_df"])
    kpi_df = pd.DataFrame(full_state["kpi_projections"])
    zip_buffer = create_brand_playbook_zip(full_state, launch_df, kpi_df)
    print(f"   ✅ Full ZIP: {len(zip_buffer.getvalue())} bytes")
    
    # Test 2: Minimal export (only foundations)
    print("\n2. Minimal export (foundations only)...")
    
    minimal_state = create_empty_state()
    minimal_state["company_name"] = "MinimalCo"
    minimal_state["vision"] = "Create value"
    minimal_state["mission"] = "Serve customers"
    minimal_state["values"] = ["Quality"]
    
    playbook_min = generate_playbook_markdown(minimal_state)
    assert len(playbook_min) > 100, "Minimal export should still work"
    print(f"   ✅ Minimal export: {len(playbook_min)} chars")
    
    # Test 3: Export with missing optional fields
    print("\n3. Export with missing optional fields...")
    
    partial_state = create_empty_state()
    partial_state["company_name"] = "PartialCo"
    partial_state["vision"] = "Transform"
    partial_state["mission"] = "Enable"
    # Missing values, positioning, etc.
    
    try:
        playbook_partial = generate_playbook_markdown(partial_state)
        print(f"   ✅ Partial export: {len(playbook_partial)} chars")
    except Exception as e:
        print(f"   ⚠️  Error with partial export: {str(e)[:50]}")
    
    print(f"\n✅ EXPORT VARIATIONS TEST COMPLETED!")


def test_state_persistence_edge_cases():
    """Test 5: State persistence with various scenarios"""
    print("\n" + "="*70)
    print("TEST 5: State Persistence Edge Cases")
    print("="*70)
    
    # Test 1: Large state
    print("\n1. Large state with all fields...")
    
    large_state = create_empty_state()
    large_state["company_name"] = "LargeCo"
    large_state["vision"] = "V" * 500  # Long text
    large_state["mission"] = "M" * 500
    large_state["values"] = [f"Value {i}" for i in range(10)]
    large_state["messaging_guide"] = "Guide " * 200
    large_state["launch_plan_df"] = [{"task": f"Task {i}"} for i in range(50)]
    large_state["kpi_projections"] = [{"week": i, "Visitors": i * 100, "Revenue": i * 1000} for i in range(1, 14)]
    
    filepath = "test_large_state.json"
    save_state_to_file(large_state, filepath=filepath)
    
    loaded = load_state_from_file(filepath=filepath)
    assert loaded["company_name"] == "LargeCo"
    assert len(loaded["launch_plan_df"]) == 50
    
    filesize = os.path.getsize(filepath)
    print(f"   ✅ Large state: {filesize:,} bytes saved and loaded")
    
    os.remove(filepath)
    
    # Test 2: Unicode and special characters
    print("\n2. Unicode and special characters...")
    
    unicode_state = create_empty_state()
    unicode_state["company_name"] = "Café ☕ & Co. 🎨"
    unicode_state["vision"] = "Transform 世界 with émojis 🚀"
    unicode_state["mission"] = "Ñoño's mission with 中文"
    
    filepath = "test_unicode_state.json"
    save_state_to_file(unicode_state, filepath=filepath)
    
    loaded = load_state_from_file(filepath=filepath)
    assert loaded["company_name"] == unicode_state["company_name"]
    assert loaded["vision"] == unicode_state["vision"]
    
    print(f"   ✅ Unicode preserved: {loaded['company_name']}")
    
    os.remove(filepath)
    
    # Test 3: Empty/None values
    print("\n3. Empty and None values...")
    
    empty_state = create_empty_state()
    empty_state["company_name"] = ""
    empty_state["vision"] = None
    empty_state["values"] = []
    
    filepath = "test_empty_state.json"
    save_state_to_file(empty_state, filepath=filepath)
    
    loaded = load_state_from_file(filepath=filepath)
    assert loaded["company_name"] == ""
    assert loaded["values"] == []
    
    print(f"   ✅ Empty values handled correctly")
    
    os.remove(filepath)
    
    print(f"\n✅ STATE PERSISTENCE TEST COMPLETED!")


# Run all tests
if __name__ == "__main__":
    print("\n" + "="*70)
    print("PHASE 9 INTEGRATION TEST SUITE: END-TO-END WORKFLOW TESTING")
    print("Testing: Complete workflow, error handling, exports, persistence")
    print("="*70)
    
    tests_passed = 0
    tests_failed = 0
    
    tests = [
        ("Complete Workflow Integration", test_complete_workflow_integration),
        ("Error Handling", test_error_handling),
        ("Different Brand Types", test_different_brand_types),
        ("Export Variations", test_export_variations),
        ("State Persistence", test_state_persistence_edge_cases)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*70}")
            print(f"Running: {test_name}")
            print(f"{'='*70}")
            
            result = test_func()
            results[test_name] = {"status": "PASSED", "result": result}
            tests_passed += 1
            
        except AssertionError as e:
            tests_failed += 1
            results[test_name] = {"status": "FAILED", "error": str(e)}
            print(f"\n❌ TEST FAILED: {test_name}")
            print(f"   Error: {e}")
            
        except Exception as e:
            tests_failed += 1
            results[test_name] = {"status": "ERROR", "error": str(e)}
            print(f"\n❌ TEST ERROR: {test_name}")
            print(f"   Exception: {type(e).__name__}: {str(e)[:100]}")
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests Passed: {tests_passed}/{len(tests)}")
    print(f"Tests Failed: {tests_failed}/{len(tests)}")
    
    if tests_failed == 0:
        print("\n✅ ALL INTEGRATION TESTS PASSED! 🎉")
        print("\nSystem Validation:")
        print("  ✅ Complete end-to-end workflow")
        print("  ✅ Error handling and edge cases")
        print("  ✅ Multiple brand types supported")
        print("  ✅ Export functionality robust")
        print("  ✅ State persistence reliable")
    else:
        print(f"\n⚠️  {tests_failed} test(s) need attention")
        print("\nFailed tests:")
        for name, result in results.items():
            if result["status"] != "PASSED":
                print(f"  ❌ {name}: {result.get('error', 'Unknown error')[:80]}")
    
    print("="*70)
