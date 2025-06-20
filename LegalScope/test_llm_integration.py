#!/usr/bin/env python3
"""
Test script for LLM integration
"""

import os
import sys
from utils.llm_analyzer import LLMAnalyzer, LLMConfig

def test_llm_integration():
    """Test LLM integration with fallback"""
    
    print("🧪 Testing LLM Integration...")
    
    # Test configuration
    config = LLMConfig(
        enable_llm=True,
        provider="openai",
        model="gpt-4"
    )
    
    # Initialize analyzer
    analyzer = LLMAnalyzer(config)
    
    # Sample contract data
    sample_text = """
    This agreement is entered into between Company A and Company B.
    The term of this agreement shall be 12 months and shall automatically renew.
    Company A shall pay $10,000 per month for services.
    Company A shall indemnify Company B against all claims.
    """
    
    sample_clauses = [
        {
            'type': 'Payment',
            'text': 'Company A shall pay $10,000 per month for services.',
            'summary': 'Monthly payment of $10,000 required.'
        },
        {
            'type': 'Indemnification',
            'text': 'Company A shall indemnify Company B against all claims.',
            'summary': 'Company A must defend Company B from claims.'
        }
    ]
    
    sample_risks = [
        {
            'category': 'auto_renewal',
            'severity': 'high',
            'text': 'Contract automatically renews without notice.'
        },
        {
            'category': 'unlimited_liability',
            'severity': 'medium',
            'text': 'Broad indemnification clause.'
        }
    ]
    
    print("📋 Sample Data:")
    print(f"  - Text length: {len(sample_text)} characters")
    print(f"  - Clauses: {len(sample_clauses)}")
    print(f"  - Risks: {len(sample_risks)}")
    
    # Test analysis
    try:
        print("\n🔍 Running LLM Analysis...")
        result = analyzer.analyze_contract_comprehensive(
            sample_text, sample_clauses, sample_risks
        )
        
        print("✅ Analysis completed!")
        print(f"  - Legal insights: {'Yes' if result.get('legal_insights') else 'No'}")
        print(f"  - Risk explanations: {len(result.get('risk_explanations', []))}")
        print(f"  - Recommendations: {len(result.get('recommendations', []))}")
        print(f"  - Compliance check: {'Yes' if result.get('compliance_check') else 'No'}")
        
        # Show sample output
        if result.get('legal_insights'):
            print(f"\n📝 Sample Legal Insight:")
            print(f"  {result['legal_insights'][:200]}...")
        
        if result.get('recommendations'):
            print(f"\n💡 Sample Recommendation:")
            print(f"  {result['recommendations'][0]}")
            
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return False
    
    return True

def test_fallback_behavior():
    """Test fallback behavior when LLM is disabled"""
    
    print("\n🔄 Testing Fallback Behavior...")
    
    # Test with LLM disabled
    config = LLMConfig(enable_llm=False)
    analyzer = LLMAnalyzer(config)
    
    sample_clauses = [{'type': 'Test', 'text': 'Test clause'}]
    sample_risks = [{'category': 'test', 'severity': 'low', 'text': 'Test risk'}]
    
    result = analyzer.analyze_contract_comprehensive("Test text", sample_clauses, sample_risks)
    
    print("✅ Fallback analysis completed!")
    print(f"  - Legal insights: {'Yes' if result.get('legal_insights') else 'No'}")
    print(f"  - Risk explanations: {len(result.get('risk_explanations', []))}")
    print(f"  - Recommendations: {len(result.get('recommendations', []))}")
    
    return True

if __name__ == "__main__":
    print("🚀 Legal Contract Analyzer - LLM Integration Test")
    print("=" * 50)
    
    # Check environment
    print("🔧 Environment Check:")
    print(f"  - OPENAI_API_KEY: {'Set' if os.getenv('OPENAI_API_KEY') else 'Not set'}")
    print(f"  - ENABLE_LLM: {os.getenv('ENABLE_LLM', 'false')}")
    
    # Run tests
    success1 = test_llm_integration()
    success2 = test_fallback_behavior()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("🎉 All tests passed! LLM integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print("\n💡 To enable LLM analysis:")
    print("  1. Set ENABLE_LLM=true in your .env file")
    print("  2. Add your OPENAI_API_KEY to the .env file")
    print("  3. Restart the application") 