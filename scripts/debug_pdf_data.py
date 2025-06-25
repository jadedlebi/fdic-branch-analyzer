#!/usr/bin/env python3
"""
Debug script to examine PDF data structure and calculations.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from report_builder import build_report_from_data
from pdf_report_generator import ModernPDFReportGenerator

def debug_pdf_data():
    """Debug the PDF data structure and calculations."""
    print("🔍 Debugging PDF Data Structure...")
    
    # Load sample data (you can replace this with actual data loading)
    # For now, let's create a simple test to verify the structure
    
    # Test the percentage formatting
    from pdf_report_generator import ModernPDFReportGenerator
    
    # Create a dummy generator to test formatting
    dummy_data = pd.DataFrame({
        'county_state': ['Test County'],
        'year': [2024],
        'bank_name': ['Test Bank'],
        'total_branches': [100],
        'lmict': [25],
        'mmct': [50]
    })
    
    generator = ModernPDFReportGenerator(dummy_data, ['Test County'], [2024])
    
    print("\n📊 Testing Percentage Formatting:")
    test_percentages = [25.5, 1234.56, 0.123, 100.0, 0.0]
    for pct in test_percentages:
        formatted = generator.format_percentage(pct)
        print(f"  {pct} -> {formatted}")
    
    print("\n📋 Testing Number Formatting:")
    test_numbers = [1234, 1234.56, 0.123, 1000000, 0]
    for num in test_numbers:
        formatted = generator.format_number(num)
        print(f"  {num} -> {formatted}")
    
    print("\n✅ Debug Complete!")

if __name__ == "__main__":
    debug_pdf_data() 