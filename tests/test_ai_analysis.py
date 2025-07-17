#!/usr/bin/env python3
"""
Test script for AI-powered analysis functionality.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

from analysis.gpt_utils import AIAnalyzer
import json

def test_ai_analysis():
    """Test the AI analysis functionality with sample data."""
    print("🧪 Testing AI Analysis Functionality...")
    
    # Initialize the AI analyzer
    analyzer = AIAnalyzer()
    
    # Sample data for testing
    sample_data = {
        'county': 'Montgomery County, Maryland',
        'years': [2018, 2019, 2020, 2021, 2022, 2023, 2024],
        'trends': [
            {
                'year': 2018,
                'total_branches': 288,
                'lmict': 73,
                'mmct': 132,
                'lmict_pct': 25.35,
                'mmct_pct': 45.83
            },
            {
                'year': 2024,
                'total_branches': 218,
                'lmict': 65,
                'mmct': 126,
                'lmict_pct': 29.82,
                'mmct_pct': 57.80
            }
        ],
        'market_shares': [
            {
                'bank_name': 'Truist Bank',
                'total_branches': 27,
                'market_share': 12.39,
                'lmict_pct': 29.63,
                'mmct_pct': 59.26
            },
            {
                'bank_name': 'Bank of America',
                'total_branches': 24,
                'market_share': 11.01,
                'lmict_pct': 33.33,
                'mmct_pct': 62.50
            }
        ],
        'bank_analysis': [
            {
                'bank_name': 'Truist Bank',
                'first_year_branches': 49,
                'last_year_branches': 27,
                'growth_pct': -44.90
            },
            {
                'bank_name': 'Bank of America',
                'first_year_branches': 30,
                'last_year_branches': 24,
                'growth_pct': -20.00
            }
        ],
        'comparisons': {
            'county_avg_lmict': 29.82,
            'county_avg_mmct': 57.80,
            'bank_avg_lmict': 31.48,
            'bank_avg_mmct': 60.88
        }
    }
    
    print("\n📊 Testing Overall Trends Analysis...")
    trends_analysis = analyzer.analyze_overall_trends(sample_data)
    if trends_analysis:
        print("✅ Overall trends analysis generated successfully")
        print(f"Length: {len(trends_analysis)} characters")
        print(f"Preview: {trends_analysis[:200]}...")
    else:
        print("❌ Failed to generate overall trends analysis")
    
    print("\n🏦 Testing Bank Strategy Analysis...")
    strategy_analysis = analyzer.analyze_bank_strategies(sample_data)
    if strategy_analysis:
        print("✅ Bank strategy analysis generated successfully")
        print(f"Length: {len(strategy_analysis)} characters")
        print(f"Preview: {strategy_analysis[:200]}...")
    else:
        print("❌ Failed to generate bank strategy analysis")
    
    print("\n🏘️ Testing Community Impact Analysis...")
    impact_analysis = analyzer.analyze_community_impact(sample_data)
    if impact_analysis:
        print("✅ Community impact analysis generated successfully")
        print(f"Length: {len(impact_analysis)} characters")
        print(f"Preview: {impact_analysis[:200]}...")
    else:
        print("❌ Failed to generate community impact analysis")
    
    print("\n📝 Testing Conclusion Generation...")
    conclusion = analyzer.generate_conclusion(sample_data)
    if conclusion:
        print("✅ Conclusion generated successfully")
        print(f"Length: {len(conclusion)} characters")
        print(f"Preview: {conclusion[:200]}...")
    else:
        print("❌ Failed to generate conclusion")
    
    print("\n🎉 AI Analysis Testing Complete!")
    
    # Save sample analysis to file for review
    sample_analysis = {
        'overall_trends': trends_analysis,
        'bank_strategies': strategy_analysis,
        'community_impact': impact_analysis,
        'conclusion': conclusion
    }
    
    with open('data/output/sample_ai_analysis.json', 'w') as f:
        json.dump(sample_analysis, f, indent=2)
    
    print("💾 Sample analysis saved to: data/output/sample_ai_analysis.json")

if __name__ == "__main__":
    test_ai_analysis() 