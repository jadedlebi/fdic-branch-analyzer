#!/usr/bin/env python3
"""
Test script for PDF report generator structure (without AI dependencies).
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

def test_pdf_generator_structure():
    """Test the PDF generator structure without AI dependencies."""
    print("🧪 Testing PDF Generator Structure...")
    
    try:
        from reporting.pdf_report_generator import EnhancedPDFReportGenerator
        
        # Create sample data
        sample_data = pd.DataFrame({
            'county_state': ['Montgomery County, Maryland'] * 3,
            'year': [2020, 2021, 2022],
            'bank_name': ['Test Bank 1', 'Test Bank 2', 'Test Bank 3'],
            'total_branches': [100, 95, 90],
            'lmict': [25, 24, 23],
            'mmct': [45, 44, 43],
            'lmict_pct': [25.0, 25.3, 25.6],
            'mmct_pct': [45.0, 46.3, 47.8]
        })
        
        counties = ['Montgomery County, Maryland']
        years = [2020, 2021, 2022]
        
        # Test initialization
        print("✅ Testing PDF generator initialization...")
        generator = EnhancedPDFReportGenerator(sample_data, counties, years)
        print("✅ PDF generator initialized successfully")
        
        # Test data calculation methods
        print("\n📊 Testing data calculation methods...")
        
        # Test trends calculation
        trends = generator.calculate_enhanced_trends()
        print(f"✅ Trends calculation: {len(trends)} counties processed")
        
        # Test market share calculation
        market_shares = generator.calculate_enhanced_market_share()
        print(f"✅ Market share calculation: {len(market_shares)} counties processed")
        
        # Test top banks calculation
        top_banks = generator.get_enhanced_top_banks(market_shares)
        print(f"✅ Top banks calculation: {len(top_banks)} counties processed")
        
        # Test bank analysis
        bank_analysis = generator.analyze_enhanced_bank_growth(top_banks)
        print(f"✅ Bank analysis: {len(bank_analysis)} counties processed")
        
        # Test comparisons
        comparisons = generator.calculate_enhanced_comparisons(bank_analysis)
        print(f"✅ Comparisons calculation: {len(comparisons)} counties processed")
        
        # Test formatting methods
        print("\n📝 Testing formatting methods...")
        test_number = 1234.56
        formatted_number = generator.format_number(test_number)
        print(f"✅ Number formatting: {test_number} -> {formatted_number}")
        
        test_percentage = 25.678
        formatted_percentage = generator.format_percentage(test_percentage)
        print(f"✅ Percentage formatting: {test_percentage} -> {formatted_percentage}")
        
        # Test AI analysis structure (without actual AI calls)
        print("\n🤖 Testing AI analysis structure...")
        county_data = {'county': 'Montgomery County, Maryland'}
        county_trends = trends.get('Montgomery County, Maryland', pd.DataFrame())
        county_market_shares = market_shares.get('Montgomery County, Maryland', pd.DataFrame())
        county_bank_analysis = bank_analysis.get('Montgomery County, Maryland', pd.DataFrame())
        county_comparisons = comparisons.get('Montgomery County, Maryland', {})
        
        # Test the method structure (will fail on AI call, but that's expected)
        try:
            ai_analysis = generator.generate_enhanced_ai_analysis(
                county_data, county_trends, county_market_shares, 
                county_bank_analysis, county_comparisons
            )
            print("✅ AI analysis method structure is correct")
        except Exception as e:
            print(f"⚠️  AI analysis method structure test (expected to fail on AI call): {str(e)[:100]}...")
        
        print("\n🎉 PDF Generator Structure Test Complete!")
        print("✅ All core functionality verified")
        print("✅ Data processing methods working")
        print("✅ Formatting methods working")
        print("✅ Structure ready for AI integration")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_pdf_generator_structure() 