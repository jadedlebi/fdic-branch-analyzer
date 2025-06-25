#!/usr/bin/env python3
"""
AI-assisted FDIC Bank Branch Report Generator
Main orchestration script for the complete workflow.
"""

import sys
import os
from datetime import datetime
from typing import List, Dict
import pandas as pd

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.bq_utils import execute_query, find_exact_county_match
from analysis.gpt_utils import AIAnalyzer, ask_gpt, extract_parameters
from reporting.pdf_report_generator import generate_pdf_report_from_data
from reporting.report_builder import build_report, save_excel_report

# Import configuration
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'config'))
from config import *

from config import PROMPT_PATH, SQL_TEMPLATE_PATH, OUTPUT_DIR


def load_prompt() -> str:
    """Load the natural language prompt from file."""
    try:
        with open(PROMPT_PATH, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"Error: Prompt file not found at {PROMPT_PATH}")
        sys.exit(1)


def load_sql_template() -> str:
    """Load the SQL query template from file."""
    try:
        with open(SQL_TEMPLATE_PATH, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"Error: SQL template file not found at {SQL_TEMPLATE_PATH}")
        sys.exit(1)


def select_county_interactively(user_county: str) -> str:
    """Prompt the user to clarify or select the correct county if ambiguous."""
    matches = find_exact_county_match(user_county)
    if not matches:
        print(f"❌ No counties found matching '{user_county}'. Please check the spelling or use the county_reference.py script to find the exact name.")
        new_county = input(f"Enter the exact county name (e.g., 'Cook County, Illinois'): ").strip()
        return select_county_interactively(new_county)
    elif len(matches) == 1:
        print(f"✅ Using county: {matches[0]}")
        return matches[0]
    else:
        print(f"⚠️  Multiple counties found for '{user_county}':")
        for idx, match in enumerate(matches, 1):
            print(f"  {idx}. {match}")
        while True:
            try:
                choice = int(input(f"Select the correct county [1-{len(matches)}]: "))
                if 1 <= choice <= len(matches):
                    print(f"✅ Using county: {matches[choice-1]}")
                    return matches[choice-1]
            except Exception:
                pass
            print("Invalid selection. Please enter a valid number.")


def get_user_parameters():
    print("Enter counties (semicolon-separated, e.g. 'Queens County, New York; Cook County, Illinois'):")
    counties_input = input("> ").strip()
    counties = [c.strip() for c in counties_input.split(";") if c.strip()]

    print("Enter years (comma-separated, e.g. '2020,2021,2022' or 'all' for 2017-2024):")
    years_input = input("> ").strip()
    if years_input.lower() == "all":
        years = list(range(2017, 2025))
    else:
        years = [int(y.strip()) for y in years_input.split(",") if y.strip().isdigit()]

    return counties, years


def prepare_data_for_pdf(raw_data: pd.DataFrame) -> pd.DataFrame:
    """Prepare the raw data for PDF generation by adding required percentage fields."""
    # Convert to DataFrame if it's not already
    if not isinstance(raw_data, pd.DataFrame):
        raw_data = pd.DataFrame(raw_data)
    
    # Ensure numeric columns
    numeric_columns = ['total_branches', 'lmict', 'mmct']
    for col in numeric_columns:
        raw_data[col] = pd.to_numeric(raw_data[col], errors='coerce').fillna(0)
    
    # Calculate percentage fields that the PDF generator expects
    raw_data['lmict_pct'] = (raw_data['lmict'] / raw_data['total_branches'] * 100).round(2)
    raw_data['mmct_pct'] = (raw_data['mmct'] / raw_data['total_branches'] * 100).round(2)
    
    # Handle division by zero
    raw_data['lmict_pct'] = raw_data['lmict_pct'].fillna(0)
    raw_data['mmct_pct'] = raw_data['mmct_pct'].fillna(0)
    
    return raw_data


def main():
    """Main workflow orchestration."""
    print("🚀 Starting AI-assisted FDIC bank branch report generator...")
    
    # Step 1: Get user parameters
    print("\n📝 Step 1: Enter counties and years for the report...")
    counties, years = get_user_parameters()
    print(f"Counties: {counties}")
    print(f"Years: {years}")

    # Step 2: Clarify county selections once
    print("\n🔍 Step 2: Clarifying county selections...")
    clarified_counties = []
    for county in counties:
        clarified_county = select_county_interactively(county)
        clarified_counties.append(clarified_county)
    
    print(f"Clarified counties: {clarified_counties}")

    # Step 3: Execute BigQuery for each county/year combination
    print("\n🔍 Step 3: Executing BigQuery queries...")
    sql_template = load_sql_template()
    all_results = []
    
    for county in clarified_counties:
        for year in years:
            print(f"  Querying {county} for year {year}...")
            try:
                results = execute_query(sql_template, county, year)
                all_results.extend(results)
                print(f"    Found {len(results)} records")
            except Exception as e:
                print(f"    Error querying {county} {year}: {e}")
                continue

    if not all_results:
        print("❌ No data found for the specified parameters")
        sys.exit(1)

    # Step 4: Build and save report
    print(f"\n📊 Step 4: Building report with {len(all_results)} records...")
    try:
        report_data = build_report(all_results, clarified_counties, years)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        counties_str = "_".join(clarified_counties).replace(" ", "_").replace(",", "")
        years_str = "_".join(map(str, years))
        filename = f"fdic_branch_report_{counties_str}_{years_str}_{timestamp}.xlsx"
        
        output_path = os.path.join(OUTPUT_DIR, filename)
        save_excel_report(report_data, output_path)
        print(f"✅ Report saved successfully: {output_path}")
        
        # Prepare data for PDF generation
        pdf_data = prepare_data_for_pdf(report_data['raw_data'])
        
        # PDF report generation
        pdf_output_path = output_path.replace('.xlsx', '.pdf')
        print(f"\n📝 Generating PDF report...")
        generate_pdf_report_from_data(pdf_data, clarified_counties, years, pdf_output_path)
        print(f"✅ PDF report saved successfully: {pdf_output_path}")
        
    except Exception as e:
        print(f"Error building report: {e}")
        sys.exit(1)
    
    print("\n🎉 Report generation completed successfully!")


if __name__ == "__main__":
    main()
