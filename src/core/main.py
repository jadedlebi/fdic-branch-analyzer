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


def select_county_automatically(user_county: str) -> str:
    """Automatically select the best county match without user interaction."""
    matches = find_exact_county_match(user_county)
    if not matches:
        raise ValueError(f"No counties found matching '{user_county}'. Please check the spelling.")
    elif len(matches) == 1:
        return matches[0]
    else:
        # For web interface, return the first match and log the ambiguity
        print(f"Warning: Multiple counties found for '{user_county}', using first match: {matches[0]}")
        return matches[0]


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


def parse_web_parameters(counties_str: str, years_str: str) -> tuple:
    """Parse parameters from web interface."""
    counties = [c.strip() for c in counties_str.split(";") if c.strip()]
    
    if years_str.lower() == "all":
        years = list(range(2017, 2025))
    else:
        years = [int(y.strip()) for y in years_str.split(",") if y.strip().isdigit()]
    
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


def run_analysis(counties_str: str, years_str: str, run_id: str = None, progress_tracker=None) -> Dict:
    """Run analysis for web interface. Returns a dictionary with success/error status."""
    try:
        # Initialize progress
        if progress_tracker:
            progress_tracker.update_progress('initializing')
        
        # Parse parameters
        counties, years = parse_web_parameters(counties_str, years_str)
        
        if progress_tracker:
            progress_tracker.update_progress('parsing_params')
        
        if not counties:
            return {'success': False, 'error': 'No counties provided'}
        
        if not years:
            return {'success': False, 'error': 'No years provided'}
        
        # Clarify county selections automatically
        if progress_tracker:
            progress_tracker.update_progress('clarifying_counties')
        
        clarified_counties = []
        for county in counties:
            try:
                clarified_county = select_county_automatically(county)
                clarified_counties.append(clarified_county)
            except ValueError as e:
                return {'success': False, 'error': str(e)}
        
        # Execute BigQuery queries with tracking if run_id provided
        if progress_tracker:
            progress_tracker.update_progress('connecting_bq')
        
        sql_template = load_sql_template()
        all_results = []
        
        if run_id:
            # Use tracked BigQuery client
            from src.utils.bq_tracker import TrackedBigQueryClient
            bq_client = TrackedBigQueryClient(run_id, progress_tracker)
            
            # Calculate total queries for progress tracking
            total_queries = len(clarified_counties) * len(years)
            query_index = 0
            
            for county in clarified_counties:
                for year in years:
                    try:
                        results = bq_client.execute_query(sql_template, county, year, query_index, total_queries)
                        all_results.extend(results)
                        query_index += 1
                    except Exception as e:
                        print(f"Error querying {county} {year}: {e}")
                        query_index += 1
                        continue
        else:
            # Use regular BigQuery client
            for county in clarified_counties:
                for year in years:
                    try:
                        results = execute_query(sql_template, county, year)
                        all_results.extend(results)
                    except Exception as e:
                        print(f"Error querying {county} {year}: {e}")
                        continue
        
        if not all_results:
            return {'success': False, 'error': 'No data found for the specified parameters'}
        
        # Build and save report
        if progress_tracker:
            progress_tracker.update_progress('building_report')
        
        report_data = build_report(all_results, clarified_counties, years)
        
        # Save Excel report with standard filename
        excel_path = os.path.join(OUTPUT_DIR, 'fdic_branch_analysis.xlsx')
        save_excel_report(report_data, excel_path)
        
        # Update run metadata with file paths
        if run_id:
            from src.utils.run_logger import run_logger
            run_logger.update_run(run_id, excel_file=excel_path)
        
        # Prepare data for PDF generation
        if progress_tracker:
            progress_tracker.update_progress('preparing_pdf')
        
        pdf_data = prepare_data_for_pdf(report_data['raw_data'])
        
        # Generate PDF report with AI analysis if run_id provided
        pdf_path = os.path.join(OUTPUT_DIR, 'fdic_branch_analysis.pdf')
        
        if run_id:
            # Use tracked AI analyzer
            from src.analysis.ai_tracker import TrackedAIAnalyzer
            ai_analyzer = TrackedAIAnalyzer(run_id, progress_tracker)
            
            # Create data dictionary with DataFrame and metadata for AI analysis
            ai_data = {
                'data': pdf_data,
                'counties': clarified_counties,
                'years': years,
                'total_branches': len(pdf_data),
                'top_banks': pdf_data['bank_name'].value_counts().head(5).index.tolist() if 'bank_name' in pdf_data.columns else []
            }
            
            # Generate AI analysis sections
            if progress_tracker:
                progress_tracker.update_progress('generating_ai')
            
            ai_sections = {
                'executive_summary': ai_analyzer.generate_executive_summary(ai_data),
                'key_findings': ai_analyzer.generate_key_findings(ai_data),
                'trends_analysis': ai_analyzer.generate_trends_analysis(ai_data),
                'bank_strategies': ai_analyzer.generate_bank_strategies_analysis(ai_data),
                'community_impact': ai_analyzer.generate_community_impact_analysis(ai_data),
                'conclusion': ai_analyzer.generate_conclusion(ai_data)
            }
            
            # Generate PDF with AI analysis
            if progress_tracker:
                progress_tracker.update_progress('creating_pdf')
            
            generate_pdf_report_from_data(pdf_data, clarified_counties, years, pdf_path, ai_sections)
        else:
            # Generate PDF without AI analysis
            if progress_tracker:
                progress_tracker.update_progress('creating_pdf')
            
            generate_pdf_report_from_data(pdf_data, clarified_counties, years, pdf_path)
        
        # Update run metadata with PDF file path
        if run_id:
            run_logger.update_run(run_id, pdf_file=pdf_path)
        
        # Mark as completed
        if progress_tracker:
            progress_tracker.complete(success=True)
        
        return {
            'success': True,
            'message': f'Analysis completed successfully. Generated reports for {len(clarified_counties)} counties and {len(years)} years.',
            'counties': clarified_counties,
            'years': years,
            'records': len(all_results)
        }
        
    except Exception as e:
        if progress_tracker:
            progress_tracker.complete(success=False, error=str(e))
        return {'success': False, 'error': f'Analysis failed: {str(e)}'}


def main():
    """Main workflow orchestration."""
    print("🚀 Starting AI-assisted FDIC bank branch report generator...")
    
    # Step 1: Get user parameters
    print("\n📝 Step 1: Enter counties and years for the report...")
    counties, years = get_user_parameters()
    print(f"Counties: {counties}")
    print(f"Years: {years}")

    # Set up Google Cloud credentials for BigQuery logging
    try:
        from scripts.setup_gcp_credentials import setup_environment
        setup_environment()
    except ImportError:
        print("Warning: Could not set up GCP credentials for logging")
    
    # Start run logging for CLI
    from src.utils.run_logger import run_logger
    run_id = run_logger.start_run(
        counties=counties,
        years=years,
        interface_type="cli"
    )

    try:
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
        
        # Use tracked BigQuery client
        from src.utils.bq_tracker import TrackedBigQueryClient
        bq_client = TrackedBigQueryClient(run_id)
        
        for county in clarified_counties:
            for year in years:
                print(f"  Querying {county} for year {year}...")
                try:
                    results = bq_client.execute_query(sql_template, county, year)
                    all_results.extend(results)
                    print(f"    Found {len(results)} records")
                except Exception as e:
                    print(f"    Error querying {county} {year}: {e}")
                    continue

        if not all_results:
            print("❌ No data found for the specified parameters")
            run_logger.end_run(run_id, success=False, error_message="No data found for the specified parameters")
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
            
            # Update run metadata with Excel file path
            run_logger.update_run(run_id, excel_file=output_path)
            
            # Prepare data for PDF generation
            pdf_data = prepare_data_for_pdf(report_data['raw_data'])
            
            # PDF report generation with AI analysis
            pdf_output_path = output_path.replace('.xlsx', '.pdf')
            print(f"\n📝 Generating PDF report...")
            
            # Use tracked AI analyzer
            from src.analysis.ai_tracker import TrackedAIAnalyzer
            ai_analyzer = TrackedAIAnalyzer(run_id)
            
            # Create data dictionary with DataFrame and metadata for AI analysis
            ai_data = {
                'data': pdf_data,
                'counties': clarified_counties,
                'years': years,
                'total_branches': len(pdf_data),
                'top_banks': pdf_data['bank_name'].value_counts().head(5).index.tolist() if 'bank_name' in pdf_data.columns else []
            }
            
            # Generate AI analysis sections
            ai_sections = {
                'executive_summary': ai_analyzer.generate_executive_summary(ai_data),
                'key_findings': ai_analyzer.generate_key_findings(ai_data),
                'trends_analysis': ai_analyzer.generate_trends_analysis(ai_data),
                'bank_strategies': ai_analyzer.generate_bank_strategies_analysis(ai_data),
                'community_impact': ai_analyzer.generate_community_impact_analysis(ai_data),
                'conclusion': ai_analyzer.generate_conclusion(ai_data)
            }
            
            # Generate PDF with AI analysis
            generate_pdf_report_from_data(pdf_data, clarified_counties, years, pdf_output_path, ai_sections)
            print(f"✅ PDF report saved successfully: {pdf_output_path}")
            
            # Update run metadata with PDF file path
            run_logger.update_run(run_id, pdf_file=pdf_output_path)
            
            # End the run successfully
            run_logger.end_run(run_id, success=True)
            
        except Exception as e:
            error_msg = f"Error building report: {e}"
            print(error_msg)
            run_logger.end_run(run_id, success=False, error_message=error_msg)
            sys.exit(1)
        
        print("\n🎉 Report generation completed successfully!")
        
    except Exception as e:
        error_msg = f"Analysis failed: {str(e)}"
        print(error_msg)
        run_logger.end_run(run_id, success=False, error_message=error_msg)
        sys.exit(1)


if __name__ == "__main__":
    main()
