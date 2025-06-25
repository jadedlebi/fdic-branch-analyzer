#!/usr/bin/env python3
"""
Debug script to test PDF generation with actual data
"""

import pandas as pd
import os
from pdf_report_generator import generate_pdf_report_from_data

def debug_pdf_generation():
    """Debug the PDF generation process."""
    
    # Find the most recent Excel file
    output_dir = "data/output"
    excel_files = [f for f in os.listdir(output_dir) if f.endswith('.xlsx')]
    
    if not excel_files:
        print("No Excel files found in output directory")
        return
    
    # Get the most recent file
    latest_file = sorted(excel_files)[-1]
    excel_path = os.path.join(output_dir, latest_file)
    
    print(f"Using Excel file: {excel_path}")
    
    # Read the raw data from the Excel file
    try:
        raw_data = pd.read_excel(excel_path, sheet_name='Raw Data')
        print(f"✅ Loaded raw data: {raw_data.shape}")
        print(f"Columns: {list(raw_data.columns)}")
        print(f"First few rows:")
        print(raw_data.head())
        
        # Check for required columns
        required_columns = ['bank_name', 'year', 'county_state', 'total_branches', 'lmict', 'mmct']
        missing_columns = [col for col in required_columns if col not in raw_data.columns]
        if missing_columns:
            print(f"❌ Missing required columns: {missing_columns}")
            return
        
        # Extract counties and years from the data
        counties = raw_data['county_state'].unique().tolist()
        years = sorted(raw_data['year'].unique().tolist())
        
        print(f"Counties found: {counties}")
        print(f"Years found: {years}")
        
        # Check data quality
        print(f"\nData quality check:")
        print(f"Total records: {len(raw_data)}")
        print(f"Records with total_branches > 0: {len(raw_data[raw_data['total_branches'] > 0])}")
        print(f"Records with lmict > 0: {len(raw_data[raw_data['lmict'] > 0])}")
        print(f"Records with mmct > 0: {len(raw_data[raw_data['mmct'] > 0])}")
        
        # Test PDF generation
        pdf_path = excel_path.replace('.xlsx', '_debug.pdf')
        print(f"\nGenerating debug PDF: {pdf_path}")
        
        generate_pdf_report_from_data(raw_data, counties, years, pdf_path)
        
        # Check if PDF was created and has content
        if os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            print(f"✅ PDF created: {pdf_path} ({file_size} bytes)")
            
            if file_size < 1000:
                print("⚠️  PDF file is very small - may be empty")
            else:
                print("✅ PDF appears to have content")
        else:
            print("❌ PDF file was not created")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_pdf_generation() 