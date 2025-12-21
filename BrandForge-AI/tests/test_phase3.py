"""
Test Phase 3: LangGraph Workflow Integration
Tests the complete workflow orchestration system
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add modules to path
sys.path.append(str(Path(__file__).parent))

from modules.state import create_empty_state
from modules.workflow import (
    BrandWorkflowExecutor,
    create_brand_workflow,
    get_workflow_progress,
    can_execute_step
)
from modules.graph_nodes import execute_node

# Load environment variables
load_dotenv()


def print_section(title: str):
    """Print formatted section header."""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80 + "\n")


def test_workflow_creation():
    """Test 1: Workflow Compilation"""
    print_section("TEST 1: Workflow Creation & Compilation")
    
    try:
        workflow = create_brand_workflow()
        print("✅ Workflow compiled successfully")
        print(f"   Graph type: {type(workflow).__name__}")
        return True
    except Exception as e:
        print(f"❌ Workflow creation failed: {str(e)}")
        return False


def test_workflow_executor_init():
    """Test 2: Workflow Executor Initialization"""
    print_section("TEST 2: Workflow Executor Initialization")
    
    try:
        executor = BrandWorkflowExecutor(use_flexible=False)
        print("✅ Standard workflow executor initialized")
        
        executor_flex = BrandWorkflowExecutor(use_flexible=True)
        print("✅ Flexible workflow executor initialized")
        
        return True
    except Exception as e:
        print(f"❌ Executor initialization failed: {str(e)}")
        return False


def test_single_node_execution():
    """Test 3: Single Node Execution"""
    print_section("TEST 3: Single Node Execution")
    
    try:
        # Create test state
        state = create_empty_state()
        state["company_name"] = "TechFlow AI"
        state["target_audience"] = "Software developers building AI applications"
        state["core_problem"] = "Complex infrastructure setup for production AI apps"
        state["brand_voice"] = "Professional"
        
        print("📝 Test state created:")
        print(f"   Company: {state['company_name']}")
        print(f"   Audience: {state['target_audience'][:50]}...")
        
        # Execute foundations node
        print("\n🔄 Executing foundations node...")
        updated_state = execute_node("foundations", state)
        
        # Check results
        if updated_state.get("vision") and updated_state.get("mission") and updated_state.get("values"):
            print("\n✅ Node executed successfully!")
            print(f"\n📊 Generated Results:")
            print(f"   Vision: {updated_state['vision'][:80]}...")
            print(f"   Mission: {updated_state['mission'][:80]}...")
            print(f"   Values: {len(updated_state['values'])} values generated")
            print(f"   Current Step: {updated_state.get('current_step', 0)}")
            return True
        else:
            print("❌ Node execution incomplete - missing expected fields")
            return False
            
    except Exception as e:
        print(f"❌ Node execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_workflow_progress_tracking():
    """Test 4: Workflow Progress Tracking"""
    print_section("TEST 4: Workflow Progress Tracking")
    
    try:
        # Empty state
        empty_state = create_empty_state()
        progress_empty = get_workflow_progress(empty_state)
        
        print("📊 Empty State Progress:")
        print(f"   Completed: {progress_empty['completed']}/{progress_empty['total']} steps")
        print(f"   Percentage: {progress_empty['percentage']:.1f}%")
        
        # Partially filled state
        partial_state = create_empty_state()
        partial_state["vision"] = "Test vision"
        partial_state["mission"] = "Test mission"
        partial_state["values"] = ["Value 1", "Value 2"]
        
        progress_partial = get_workflow_progress(partial_state)
        
        print("\n📊 Partial State Progress:")
        print(f"   Completed: {progress_partial['completed']}/{progress_partial['total']} steps")
        print(f"   Percentage: {progress_partial['percentage']:.1f}%")
        print(f"   Completed steps: {', '.join(progress_partial['completed_steps'])}")
        
        if progress_partial['completed'] > progress_empty['completed']:
            print("\n✅ Progress tracking working correctly")
            return True
        else:
            print("\n❌ Progress tracking not detecting changes")
            return False
            
    except Exception as e:
        print(f"❌ Progress tracking failed: {str(e)}")
        return False


def test_prerequisite_checking():
    """Test 5: Prerequisite Validation"""
    print_section("TEST 5: Prerequisite Checking")
    
    try:
        # Empty state - should fail prerequisites
        empty_state = create_empty_state()
        can_exec, message = can_execute_step("foundations", empty_state)
        
        print(f"📋 Checking foundations prerequisites on empty state:")
        print(f"   Can execute: {can_exec}")
        print(f"   Message: {message}")
        
        if not can_exec:
            print("   ✅ Correctly blocked execution")
        
        # Valid state - should pass
        valid_state = create_empty_state()
        valid_state["company_name"] = "Test Co"
        valid_state["target_audience"] = "Test audience"
        valid_state["core_problem"] = "Test problem"
        
        can_exec_valid, message_valid = can_execute_step("foundations", valid_state)
        
        print(f"\n📋 Checking foundations prerequisites on valid state:")
        print(f"   Can execute: {can_exec_valid}")
        
        if can_exec_valid:
            print("   ✅ Correctly allowed execution")
            return True
        else:
            print(f"   ❌ Incorrectly blocked: {message_valid}")
            return False
            
    except Exception as e:
        print(f"❌ Prerequisite checking failed: {str(e)}")
        return False


def test_workflow_executor_step():
    """Test 6: Workflow Executor Step-by-Step Execution"""
    print_section("TEST 6: Workflow Executor Step Execution")
    
    try:
        # Create executor
        executor = BrandWorkflowExecutor(use_flexible=False)
        
        # Create test state
        state = create_empty_state()
        state["company_name"] = "BrandForge AI"
        state["target_audience"] = "Startup founders building consumer brands"
        state["core_problem"] = "Lack of structured brand development guidance"
        state["brand_voice"] = "Professional"
        
        print("🚀 Executing foundations step via workflow executor...")
        
        updated_state = executor.execute_step("foundations", state)
        
        # Verify execution
        if updated_state.get("vision") and updated_state.get("mission"):
            print("\n✅ Workflow executor successfully executed step")
            print(f"   Execution history: {len(executor.execution_history)} steps")
            print(f"   Last step: {executor.execution_history[-1]['step']}")
            return True
        else:
            print("\n❌ Workflow executor did not update state correctly")
            return False
            
    except Exception as e:
        print(f"❌ Workflow executor failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all Phase 3 tests."""
    print("\n" + "=" * 80)
    print("🧪 BRANDFORGE AI - PHASE 3 TEST SUITE")
    print("=" * 80)
    
    tests = [
        ("Workflow Creation", test_workflow_creation),
        ("Workflow Executor Init", test_workflow_executor_init),
        ("Single Node Execution", test_single_node_execution),
        ("Progress Tracking", test_workflow_progress_tracking),
        ("Prerequisite Checking", test_prerequisite_checking),
        ("Workflow Executor Steps", test_workflow_executor_step)
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
        print("\n🎉 All tests passed! Phase 3 is fully functional.")
    else:
        print(f"\n⚠️ {total_count - passed_count} test(s) failed. Review errors above.")


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️ WARNING: GOOGLE_API_KEY not found in environment")
        print("Some tests may fail without a valid API key\n")
    
    run_all_tests()
