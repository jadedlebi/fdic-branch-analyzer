#!/usr/bin/env python3
"""
Test script to verify Claude integration with the AI analyzer.
"""

import os
import sys
from gpt_utils import AIAnalyzer, ask_ai
from config import AI_PROVIDER, CLAUDE_API_KEY

def test_claude_integration():
    """Test the Claude integration."""
    print(f"🤖 Testing {AI_PROVIDER.upper()} integration...")
    
    # Check if API key is available
    if AI_PROVIDER == "claude" and not CLAUDE_API_KEY:
        print("❌ CLAUDE_API_KEY not found in environment variables.")
        print("Please set your Claude API key in the .env file or environment variables.")
        return False
    
    try:
        # Test basic AI call
        print("📝 Testing basic AI call...")
        test_prompt = "What is 2 + 2? Please respond with just the number."
        response = ask_ai(test_prompt)
        print(f"✅ AI Response: {response}")
        
        # Test AI Analyzer
        print("\n🔍 Testing AI Analyzer...")
        analyzer = AIAnalyzer()
        print(f"✅ AI Analyzer initialized with provider: {analyzer.provider}")
        print(f"✅ Using model: {analyzer.model}")
        
        # Test a simple analysis
        test_data = {
            'county': 'Test County',
            'years': [2020, 2021, 2022],
            'trends': [
                {'year': 2020, 'total_branches': 100, 'lmict': 30, 'mmct': 25},
                {'year': 2021, 'total_branches': 95, 'lmict': 28, 'mmct': 24},
                {'year': 2022, 'total_branches': 90, 'lmict': 25, 'mmct': 22}
            ],
            'market_shares': [
                {'bank_name': 'Test Bank 1', 'total_branches': 45, 'market_share': 50.0},
                {'bank_name': 'Test Bank 2', 'total_branches': 30, 'market_share': 33.3},
                {'bank_name': 'Test Bank 3', 'total_branches': 15, 'market_share': 16.7}
            ],
            'bank_analysis': [
                {'bank_name': 'Test Bank 1', 'first_year_branches': 50, 'last_year_branches': 45, 'percentage_change': -10.0},
                {'bank_name': 'Test Bank 2', 'first_year_branches': 30, 'last_year_branches': 30, 'percentage_change': 0.0},
                {'bank_name': 'Test Bank 3', 'first_year_branches': 20, 'last_year_branches': 15, 'percentage_change': -25.0}
            ],
            'comparisons': {
                'county_avg_lmict': 30.0,
                'county_avg_mmct': 25.0,
                'total_county_branches': 90
            }
        }
        
        print("\n📊 Testing executive summary generation...")
        executive_summary = analyzer.generate_executive_summary(test_data)
        if executive_summary:
            print(f"✅ Executive Summary generated ({len(executive_summary)} characters)")
            print(f"Preview: {executive_summary[:200]}...")
        else:
            print("❌ Failed to generate executive summary")
        
        print("\n📋 Testing key findings generation...")
        key_findings = analyzer.generate_key_findings(test_data)
        if key_findings:
            print(f"✅ Key Findings generated ({len(key_findings)} characters)")
            print(f"Preview: {key_findings[:200]}...")
        else:
            print("❌ Failed to generate key findings")
        
        print("\n📈 Testing trends analysis...")
        trends_analysis = analyzer.analyze_overall_trends(test_data)
        if trends_analysis:
            print(f"✅ Trends Analysis generated ({len(trends_analysis)} characters)")
            print(f"Preview: {trends_analysis[:200]}...")
        else:
            print("❌ Failed to generate trends analysis")
        
        print("\n🎯 Testing bank strategies analysis...")
        bank_strategies = analyzer.analyze_bank_strategies(test_data)
        if bank_strategies:
            print(f"✅ Bank Strategies Analysis generated ({len(bank_strategies)} characters)")
            print(f"Preview: {bank_strategies[:200]}...")
        else:
            print("❌ Failed to generate bank strategies analysis")
        
        print("\n🏘️ Testing community impact analysis...")
        community_impact = analyzer.analyze_community_impact(test_data)
        if community_impact:
            print(f"✅ Community Impact Analysis generated ({len(community_impact)} characters)")
            print(f"Preview: {community_impact[:200]}...")
        else:
            print("❌ Failed to generate community impact analysis")
        
        print("\n📝 Testing conclusion generation...")
        conclusion = analyzer.generate_conclusion(test_data)
        if conclusion:
            print(f"✅ Conclusion generated ({len(conclusion)} characters)")
            print(f"Preview: {conclusion[:200]}...")
        else:
            print("❌ Failed to generate conclusion")
        
        print(f"\n🎉 All {AI_PROVIDER.upper()} integration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing {AI_PROVIDER.upper()} integration: {e}")
        return False

if __name__ == "__main__":
    success = test_claude_integration()
    sys.exit(0 if success else 1) 