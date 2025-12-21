"""
Test script for BrandForge AI - Phase 2
Tests Gemini API integration and all agent functions
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from modules.langchain_agents import (
    test_api_connection,
    generate_brand_foundations,
    generate_positioning_statement,
    analyze_competitors,
    generate_brand_identity
)

def test_api_connection_check():
    """Test 1: Verify API connection works"""
    print("\n" + "="*60)
    print("TEST 1: API Connection")
    print("="*60)
    
    result = test_api_connection()
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    print(f"Model: {result['model']}")
    print(f"API Key Present: {result['api_key_present']}")
    
    if result['status'] == 'success':
        print("✅ API connection test PASSED")
        return True
    else:
        print("❌ API connection test FAILED")
        print(f"Error: {result['message']}")
        return False


def test_brand_foundations():
    """Test 2: Generate brand foundations"""
    print("\n" + "="*60)
    print("TEST 2: Brand Foundations Generation")
    print("="*60)
    
    try:
        result = generate_brand_foundations(
            company_name="TechFlow AI",
            target_audience="Software developers who want to build AI applications faster",
            core_problem="Building production-ready AI apps requires too much infrastructure setup and ML expertise",
            brand_voice="Professional"
        )
        
        print("\n📊 Generated Results:")
        print(f"\nVision: {result['vision']}")
        print(f"\nMission: {result['mission']}")
        print(f"\nValues:")
        for value in result['values']:
            print(f"  - {value}")
        
        # Validate structure
        assert 'vision' in result, "Missing vision"
        assert 'mission' in result, "Missing mission"
        assert 'values' in result, "Missing values"
        assert len(result['values']) >= 3, "Not enough values"
        
        print("\n✅ Brand foundations test PASSED")
        return True, result
        
    except Exception as e:
        print(f"\n❌ Brand foundations test FAILED: {str(e)}")
        return False, None


def test_positioning_statement(values):
    """Test 3: Generate positioning statement"""
    print("\n" + "="*60)
    print("TEST 3: Positioning Statement Generation")
    print("="*60)
    
    try:
        result = generate_positioning_statement(
            company_name="TechFlow AI",
            target_audience="Software developers who want to build AI applications faster",
            core_problem="Building production-ready AI apps requires too much infrastructure setup",
            brand_voice="Professional",
            values=values
        )
        
        print(f"\n📊 Generated Positioning:\n{result}")
        
        assert len(result) > 50, "Positioning statement too short"
        
        print("\n✅ Positioning statement test PASSED")
        return True, result
        
    except Exception as e:
        print(f"\n❌ Positioning statement test FAILED: {str(e)}")
        return False, None


def test_competitor_analysis(values, positioning):
    """Test 4: Generate competitor analysis"""
    print("\n" + "="*60)
    print("TEST 4: Competitor Analysis")
    print("="*60)
    
    try:
        result = analyze_competitors(
            company_name="TechFlow AI",
            positioning_statement=positioning,
            values=values,
            target_audience="Software developers building AI apps",
            competitors=["Vercel AI", "LangChain", "Hugging Face"]
        )
        
        print(f"\n📊 Generated Analysis:\n{result[:500]}...")
        
        assert len(result) > 200, "Analysis too short"
        assert "##" in result or "**" in result, "Not formatted as markdown"
        
        print("\n✅ Competitor analysis test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Competitor analysis test FAILED: {str(e)}")
        return False


def test_brand_identity(values, positioning):
    """Test 5: Generate brand identity"""
    print("\n" + "="*60)
    print("TEST 5: Brand Identity Generation")
    print("="*60)
    
    try:
        result = generate_brand_identity(
            company_name="TechFlow AI",
            brand_voice="Professional",
            values=values,
            target_audience="Software developers",
            positioning=positioning
        )
        
        print("\n📊 Generated Identity:")
        print(f"\nColor Palette: {result.get('color_palette_desc', 'N/A')[:200]}...")
        print(f"\nFonts: {result.get('font_recommendations', 'N/A')[:200]}...")
        print(f"\nMessaging: {result.get('messaging_guide', 'N/A')[:200]}...")
        
        assert 'color_palette_desc' in result, "Missing color palette"
        assert 'font_recommendations' in result, "Missing font recommendations"
        assert 'messaging_guide' in result, "Missing messaging guide"
        
        print("\n✅ Brand identity test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Brand identity test FAILED: {str(e)}")
        return False


def run_all_tests():
    """Run complete test suite"""
    print("\n" + "="*60)
    print("🧪 BRANDFORGE AI - PHASE 2 TEST SUITE")
    print("="*60)
    
    results = []
    
    # Test 1: API Connection
    results.append(("API Connection", test_api_connection_check()))
    
    if not results[0][1]:
        print("\n❌ Cannot proceed - API connection failed")
        print("💡 Make sure your GOOGLE_API_KEY is set in .env file")
        return
    
    # Test 2: Brand Foundations
    passed, foundations = test_brand_foundations()
    results.append(("Brand Foundations", passed))
    
    if not passed:
        print("\n⚠️ Stopping tests - foundation generation failed")
        print_summary(results)
        return
    
    values = foundations['values']
    
    # Test 3: Positioning Statement
    passed, positioning = test_positioning_statement(values)
    results.append(("Positioning Statement", passed))
    
    if not passed:
        positioning = "Default positioning"
    
    # Test 4: Competitor Analysis
    results.append(("Competitor Analysis", test_competitor_analysis(values, positioning)))
    
    # Test 5: Brand Identity
    results.append(("Brand Identity", test_brand_identity(values, positioning)))
    
    # Print summary
    print_summary(results)


def print_summary(results):
    """Print test results summary"""
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<40} {status}")
    
    print("="*60)
    print(f"Total: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! Phase 2 is fully functional.")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Check errors above.")


if __name__ == "__main__":
    run_all_tests()
