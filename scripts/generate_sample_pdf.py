import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

import pandas as pd
from reporting.pdf_report_generator import generate_pdf_report_from_data

# Sample data
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
output_path = 'data/output/test_report.pdf'

generate_pdf_report_from_data(sample_data, counties, years, output_path)
print(f"PDF generated at: {output_path}") 