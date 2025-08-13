#!/usr/bin/env python3
"""
Comprehensive test script to generate a complete PDF report with realistic data.
"""

import pandas as pd
import numpy as np
from src.reporting.pdf_report_generator import generate_pdf_report_from_data
import os

def create_comprehensive_test_data():
    """Create comprehensive test data for a full PDF report."""
    np.random.seed(42)  # For reproducible results
    
    counties = ['Los Angeles County, CA', 'Cook County, IL', 'Harris County, TX']
    years = [2020, 2021, 2022]
    banks = [
        'Chase Bank', 'Bank of America', 'Wells Fargo', 'Citibank', 
        'US Bank', 'PNC Bank', 'Capital One', 'TD Bank'
    ]
    
    data = []
    for year in years:
        for county in counties:
            # Create more realistic data with growth patterns
            base_branches = np.random.randint(50, 200)
            growth_factor = 1 + (year - 2020) * 0.05  # 5% growth per year
            
            for bank in banks:
                # Vary bank sizes
                bank_size_factor = np.random.uniform(0.3, 2.0)
                total_branches = int(base_branches * growth_factor * bank_size_factor)
                
                # Ensure realistic LMI and MMCT percentages
                lmict = int(total_branches * np.random.uniform(0.2, 0.6))
                mmct = int(total_branches * np.random.uniform(0.3, 0.7))
                
                # Ensure LMI and MMCT don't exceed total branches
                lmict = min(lmict, total_branches)
                mmct = min(mmct, total_branches)
                
                total_deposits = np.random.randint(5000000, 50000000)
                
                data.append({
                    'bank_name': bank,
                    'year': year,
                    'county_state': county,
                    'total_branches': total_branches,
                    'lmict': lmict,
                    'mmct': mmct,
                    'total_deposits': total_deposits
                })
    
    return pd.DataFrame(data)

def main():
    """Main test function."""
    print("🧪 Testing Complete PDF Report Generation...")
    
    # Create comprehensive test data
    print("📊 Creating comprehensive test data...")
    test_data = create_comprehensive_test_data()
    print(f"   Created {len(test_data)} data points")
    print(f"   Counties: {test_data['county_state'].unique()}")
    print(f"   Years: {sorted(test_data['year'].unique())}")
    print(f"   Banks: {test_data['bank_name'].unique()}")
    
    # Set output path
    output_path = "complete_test_report.pdf"
    
    try:
        # Generate PDF report
        print("📄 Generating comprehensive PDF report...")
        generate_pdf_report_from_data(
            data=test_data,
            counties=['Los Angeles County, CA', 'Cook County, IL', 'Harris County, TX'],
            years=[2020, 2021, 2022],
            output_path=output_path
        )
        
        # Check if file was created
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"✅ Complete PDF generated successfully!")
            print(f"   Output file: {output_path}")
            print(f"   File size: {file_size:,} bytes")
            print(f"   File location: {os.path.abspath(output_path)}")
            print(f"   📁 This should be a comprehensive report with multiple sections")
        else:
            print("❌ PDF file was not created")
            
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
