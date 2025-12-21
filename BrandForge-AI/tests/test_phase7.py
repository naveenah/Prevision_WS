"""
Test Suite for Phase 7: Polish, Export & Completion Features
Tests the complete playbook export and workflow completion features
"""

import os
import sys
from dotenv import load_dotenv
import pandas as pd
from io import BytesIO
import zipfile

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from modules.state import BrandState, create_empty_state
from modules.utils import create_brand_playbook_zip, generate_playbook_markdown
from modules.workflow import get_workflow_progress


def test_playbook_markdown_generation():
    """Test 1: Verify playbook markdown generation"""
    print("\n" + "="*70)
    print("TEST 1: Brand Playbook Markdown Generation")
    print("="*70)
    
    try:
        # Create comprehensive test state
        test_state = {
            "company_name": "TestCo",
            "vision": "To revolutionize testing",
            "mission": "Make testing accessible",
            "values": ["Quality", "Innovation", "Speed"],
            "target_audience": "Developers and QA teams",
            "core_problem": "Testing is too complex",
            "brand_voice": "Professional",
            "positioning_statement": "We simplify software testing",
            "color_palette_desc": "Blue and white for trust",
            "font_recommendations": "Modern sans-serif",
            "messaging_guide": "Clear, technical, helpful"
        }
        
        # Generate playbook
        markdown = generate_playbook_markdown(test_state)
        
        print(f"\n✓ Playbook Generated:")
        print(f"  - Length: {len(markdown)} chars")
        print(f"  - Lines: {len(markdown.splitlines())}")
        
        # Verify content
        assert "TestCo" in markdown, "Company name missing"
        assert "Vision" in markdown or "vision" in markdown, "Vision section missing"
        assert "Mission" in markdown or "mission" in markdown, "Mission section missing"
        assert "Values" in markdown or "values" in markdown, "Values section missing"
        
        # Check for key sections
        sections_found = []
        if "vision" in markdown.lower():
            sections_found.append("Vision")
        if "mission" in markdown.lower():
            sections_found.append("Mission")
        if "values" in markdown.lower():
            sections_found.append("Values")
        if "positioning" in markdown.lower():
            sections_found.append("Positioning")
        
        print(f"  - Sections: {', '.join(sections_found)}")
        
        print("\n✅ TEST 1 PASSED: Playbook markdown generation working")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 1 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_complete_zip_export():
    """Test 2: Test complete ZIP package creation"""
    print("\n" + "="*70)
    print("TEST 2: Complete ZIP Package Export")
    print("="*70)
    
    try:
        # Create test state
        test_state = {
            "company_name": "ZipTest Inc",
            "vision": "Test vision",
            "mission": "Test mission",
            "values": ["Value1", "Value2"],
            "target_audience": "Test audience",
            "core_problem": "Test problem",
            "brand_voice": "Professional",
            "positioning_statement": "Test positioning",
            "color_palette_desc": "Test colors",
            "font_recommendations": "Test fonts",
            "messaging_guide": "Test messaging"
        }
        
        # Create test launch plan
        launch_df = pd.DataFrame({
            "week": [1, 2, 3],
            "phase": ["Phase 1", "Phase 1", "Phase 2"],
            "deliverables": ["Task 1", "Task 2", "Task 3"],
            "owner": ["Owner 1", "Owner 2", "Owner 3"],
            "status": ["Pending", "Pending", "Pending"]
        })
        
        # Create test KPI projections
        kpi_df = pd.DataFrame({
            "Week": [1, 2, 3],
            "Visitors": [1000, 1100, 1210],
            "Signups": [25, 28, 30],
            "Revenue": [500, 550, 605]
        })
        
        # Create ZIP package
        zip_buffer = create_brand_playbook_zip(test_state, launch_df, kpi_df)
        
        print(f"\n✓ ZIP Package Created:")
        print(f"  - Buffer Size: {len(zip_buffer.getvalue())} bytes")
        
        # Verify ZIP contents
        zip_buffer.seek(0)
        with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
            file_list = zip_file.namelist()
            print(f"  - Files in ZIP: {len(file_list)}")
            
            for filename in file_list:
                print(f"    • {filename}")
            
            # Verify required files
            assert "Brand_Playbook.md" in file_list, "Missing Brand_Playbook.md"
            assert "90_Day_Launch_Plan.csv" in file_list, "Missing launch plan"
            assert "KPI_Projections.csv" in file_list, "Missing KPI projections"
            assert "README.txt" in file_list, "Missing README"
            
            # Check file sizes
            for filename in file_list:
                file_info = zip_file.getinfo(filename)
                print(f"    {filename}: {file_info.file_size} bytes")
                assert file_info.file_size > 0, f"{filename} is empty"
        
        print("\n✅ TEST 2 PASSED: ZIP package creation successful")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 2 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_workflow_progress_tracking():
    """Test 3: Verify workflow progress calculation"""
    print("\n" + "="*70)
    print("TEST 3: Workflow Progress Tracking")
    print("="*70)
    
    try:
        # Test case 1: Empty state
        empty_state = create_empty_state()
        progress = get_workflow_progress(empty_state)
        
        print(f"\n✓ Empty State Progress:")
        print(f"  - Percentage: {progress['percentage']}%")
        print(f"  - Completed: {progress['completed']}/{progress['total']}")
        
        assert progress['percentage'] >= 0, "Invalid percentage"
        assert progress['completed'] == 0, "Should have 0 completed steps"
        
        # Test case 2: Partially complete state
        partial_state: BrandState = {
            "company_name": "Test Co",
            "vision": "Test vision",
            "mission": "Test mission",
            "values": ["Value1"],
            "target_audience": "Test audience",
            "core_problem": "Test problem",
            "current_step": 2
        }
        
        progress = get_workflow_progress(partial_state)
        print(f"\n✓ Partial State Progress:")
        print(f"  - Percentage: {progress['percentage']}%")
        print(f"  - Completed: {progress['completed']}/{progress['total']}")
        print(f"  - Completed Steps: {progress['completed_steps']}")
        
        assert progress['percentage'] > 0, "Should have some progress"
        assert progress['percentage'] < 100, "Should not be complete"
        
        # Test case 3: Complete state
        complete_state: BrandState = {
            "company_name": "Complete Co",
            "vision": "Vision",
            "mission": "Mission",
            "values": ["Value1"],
            "target_audience": "Audience",
            "core_problem": "Problem",
            "brand_voice": "Professional",
            "positioning_statement": "Position",
            "color_palette_desc": "Colors",
            "font_recommendations": "Fonts",
            "messaging_guide": "Messaging",
            "launch_plan_df": {},
            "kpi_projections": [],
            "current_step": 5
        }
        
        progress = get_workflow_progress(complete_state)
        print(f"\n✓ Complete State Progress:")
        print(f"  - Percentage: {progress['percentage']}%")
        print(f"  - Completed: {progress['completed']}/{progress['total']}")
        
        assert progress['percentage'] >= 50, "Complete state should have at least 50% progress"
        assert progress['completed'] >= 3, "Should have at least 3 steps completed"
        
        print("\n✅ TEST 3 PASSED: Progress tracking working correctly")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 3 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_export_without_optional_data():
    """Test 4: Test export with minimal data (no launch plan or KPIs)"""
    print("\n" + "="*70)
    print("TEST 4: Export with Minimal Data")
    print("="*70)
    
    try:
        # Minimal state
        minimal_state = {
            "company_name": "Minimal Co",
            "vision": "Simple vision",
            "mission": "Simple mission",
            "values": ["Value1"]
        }
        
        # Create ZIP with no launch plan or KPIs
        zip_buffer = create_brand_playbook_zip(minimal_state, None, None)
        
        print(f"\n✓ Minimal ZIP Created:")
        print(f"  - Buffer Size: {len(zip_buffer.getvalue())} bytes")
        
        # Verify ZIP
        zip_buffer.seek(0)
        with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
            file_list = zip_file.namelist()
            print(f"  - Files: {', '.join(file_list)}")
            
            # Should have at least playbook and README
            assert "Brand_Playbook.md" in file_list, "Missing playbook"
            assert "README.txt" in file_list, "Missing README"
            
            # Should NOT have launch plan or KPIs
            assert "90_Day_Launch_Plan.csv" not in file_list, "Should not have launch plan"
            assert "KPI_Projections.csv" not in file_list, "Should not have KPIs"
        
        print("\n✅ TEST 4 PASSED: Minimal export working correctly")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 4 FAILED: {str(e)}")
        return False


def test_zip_file_integrity():
    """Test 5: Verify ZIP file can be extracted properly"""
    print("\n" + "="*70)
    print("TEST 5: ZIP File Integrity")
    print("="*70)
    
    try:
        # Create test package
        test_state = {
            "company_name": "Integrity Test",
            "vision": "Test",
            "mission": "Test",
            "values": ["Test"]
        }
        
        zip_buffer = create_brand_playbook_zip(test_state, None, None)
        
        # Try to extract and read files
        zip_buffer.seek(0)
        with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
            # Test ZIP integrity
            bad_file = zip_file.testzip()
            if bad_file:
                raise Exception(f"Corrupted file in ZIP: {bad_file}")
            
            print(f"\n✓ ZIP Integrity Check:")
            print(f"  - ZIP is valid: ✅")
            
            # Try reading each file
            for filename in zip_file.namelist():
                content = zip_file.read(filename)
                print(f"  - {filename}: {len(content)} bytes readable")
                assert len(content) > 0, f"Empty file: {filename}"
        
        print("\n✅ TEST 5 PASSED: ZIP file integrity verified")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 5 FAILED: {str(e)}")
        return False


def run_all_tests():
    """Run all Phase 7 tests"""
    print("\n" + "="*70)
    print("PHASE 7 TEST SUITE: POLISH & EXPORT FEATURES")
    print("="*70)
    print("Testing: Playbook export, ZIP creation, workflow completion")
    print("="*70)
    
    tests = [
        test_playbook_markdown_generation,
        test_complete_zip_export,
        test_workflow_progress_tracking,
        test_export_without_optional_data,
        test_zip_file_integrity
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
        print("\n✅ ALL PHASE 7 TESTS PASSED! 🎉")
        print("\nPhase 7 Implementation Complete:")
        print("  ✓ Playbook markdown generation")
        print("  ✓ Complete ZIP package export")
        print("  ✓ Workflow progress tracking")
        print("  ✓ Export with minimal data")
        print("  ✓ ZIP file integrity verification")
        return True
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
