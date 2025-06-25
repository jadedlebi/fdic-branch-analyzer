#!/usr/bin/env python3
"""
Test script to verify PDF formatting functions work correctly.
"""

import pandas as pd
from pdf_report_generator import EnhancedPDFReportGenerator

def test_formatting_functions():
    """Test the new formatting functions with sample AI content."""
    
    # Create sample data
    sample_data = pd.DataFrame({
        'bank_name': ['Test Bank 1', 'Test Bank 2'],
        'year': [2020, 2020],
        'county_state': ['Test County, State', 'Test County, State'],
        'total_branches': [10, 5],
        'lmict': [3, 2],
        'mmct': [2, 1]
    })
    
    # Initialize generator
    generator = EnhancedPDFReportGenerator(sample_data, ['Test County, State'], [2020])
    
    # Test AI content formatting
    print("Testing AI content formatting...")
    
    # Sample AI content with various formatting
    sample_ai_content = """
**Executive Summary:**
This analysis reveals significant trends in bank branch distribution.

**Key Findings:**
1. Branch consolidation has accelerated in recent years
2. Market concentration increased by 15%
3. Community impact varies significantly by institution

**Detailed Analysis:**
• **Market Trends:** The banking sector shows clear consolidation patterns
• **Community Impact:** LMI tract coverage remains a critical concern
• **Strategic Implications:** Banks are optimizing their branch networks

**Bold Keywords:** The *consolidation* trend and **market concentration** are key factors.
"""
    
    formatted_content = generator.format_ai_content(sample_ai_content)
    print(f"Formatted content has {len(formatted_content)} elements")
    
    # Test key findings formatting
    print("\nTesting key findings formatting...")
    
    sample_key_findings = """
1. Branch count declined by 12% from 2017 to 2024
2. Market share concentration increased among top 3 banks
3. LMI tract coverage improved slightly but remains below targets
4. Digital transformation accelerated branch optimization
5. Community banking presence maintained despite consolidation
"""
    
    formatted_findings = generator.format_key_findings(sample_key_findings)
    print(f"Formatted findings has {len(formatted_findings)} elements")
    
    # Test bullet point formatting
    print("\nTesting bullet point formatting...")
    
    sample_bullets = """
• First bullet point with important information
• Second bullet point with additional details
• Third bullet point highlighting key metrics
"""
    
    formatted_bullets = generator.format_ai_content(sample_bullets)
    print(f"Formatted bullets has {len(formatted_bullets)} elements")
    
    print("\n✅ All formatting tests completed successfully!")
    
    # Print sample formatted content
    print("\nSample formatted content structure:")
    for i, element in enumerate(formatted_content[:5]):
        print(f"  {i+1}. {type(element).__name__}")

if __name__ == "__main__":
    test_formatting_functions() 