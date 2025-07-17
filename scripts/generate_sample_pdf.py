import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

import pandas as pd
from reporting.pdf_report_generator import generate_pdf_report_from_data

# Create more comprehensive sample data
sample_data = pd.DataFrame({
    'county_state': ['Montgomery County, Maryland'] * 9,
    'year': [2020, 2020, 2020, 2021, 2021, 2021, 2022, 2022, 2022],
    'bank_name': ['Bank of America', 'Wells Fargo', 'Chase Bank', 'Bank of America', 'Wells Fargo', 'Chase Bank', 'Bank of America', 'Wells Fargo', 'Chase Bank'],
    'total_branches': [45, 38, 32, 44, 37, 31, 43, 36, 30],
    'lmict': [12, 8, 6, 11, 7, 5, 10, 6, 4],
    'mmct': [18, 15, 12, 19, 16, 13, 20, 17, 14],
    'lmict_pct': [26.7, 21.1, 18.8, 25.0, 18.9, 16.1, 23.3, 16.7, 13.3],
    'mmct_pct': [40.0, 39.5, 37.5, 43.2, 43.2, 41.9, 46.5, 47.2, 46.7]
})

counties = ['Montgomery County, Maryland']
years = [2020, 2021, 2022]
output_path = 'data/output/test_report_with_page_numbers.pdf'

# Ensure output directory exists
os.makedirs(os.path.dirname(output_path), exist_ok=True)

print("Generating PDF report with page numbers...")
generate_pdf_report_from_data(sample_data, counties, years, output_path)
print(f"✅ PDF generated successfully at: {output_path}")
print("📄 The PDF should now include page numbers at the bottom center of each page") 