#!/usr/bin/env python3
"""
Generate a comprehensive spreadsheet report of all tool runs.
Includes costs, queries, user information, and performance metrics.
"""

import os
import sys
import pandas as pd
from datetime import datetime, timezone
import argparse

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.utils.run_logger import run_logger

def generate_detailed_report(output_file: str = None):
    """Generate a detailed Excel report of all runs."""
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"fdic_analyzer_runs_report_{timestamp}.xlsx"
    
    # Get runs summary
    df = run_logger.get_runs_summary()
    cost_summary = run_logger.get_cost_summary()
    
    if df.empty:
        print("No runs found in the logs.")
        return
    
    # Create Excel writer
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        
        # Sheet 1: All Runs Summary
        df.to_excel(writer, sheet_name='All Runs', index=False)
        
        # Sheet 2: Cost Analysis
        cost_data = {
            'Metric': [
                'Total Runs',
                'Successful Runs',
                'Failed Runs',
                'Success Rate (%)',
                'Total Cost (USD)',
                'AI Cost (USD)',
                'BigQuery Cost (USD)',
                'Average Cost per Run (USD)',
                'Average AI Cost per Run (USD)',
                'Average BigQuery Cost per Run (USD)'
            ],
            'Value': [
                cost_summary['total_runs'],
                cost_summary['successful_runs'],
                cost_summary['total_runs'] - cost_summary['successful_runs'],
                round((cost_summary['successful_runs'] / cost_summary['total_runs']) * 100, 2) if cost_summary['total_runs'] > 0 else 0,
                round(cost_summary['total_cost'], 4),
                round(cost_summary['ai_cost'], 4),
                round(cost_summary['bq_cost'], 4),
                round(cost_summary['avg_cost_per_run'], 4),
                round(df['ai_cost_estimate'].mean(), 4) if not df.empty else 0,
                round(df['bq_cost_estimate'].mean(), 4) if not df.empty else 0
            ]
        }
        cost_df = pd.DataFrame(cost_data)
        cost_df.to_excel(writer, sheet_name='Cost Analysis', index=False)
        
        # Sheet 3: User Analysis
        if not df.empty:
            user_analysis = []
            
            # Interface type analysis
            interface_counts = df['interface_type'].value_counts()
            for interface, count in interface_counts.items():
                user_analysis.append({
                    'Category': 'Interface Type',
                    'Value': interface,
                    'Count': count,
                    'Percentage': round((count / len(df)) * 100, 2)
                })
            
            # Browser analysis (if available)
            if 'user_agent' in df.columns:
                # Simple browser detection
                browsers = []
                for ua in df['user_agent'].dropna():
                    if 'Chrome' in ua:
                        browsers.append('Chrome')
                    elif 'Firefox' in ua:
                        browsers.append('Firefox')
                    elif 'Safari' in ua:
                        browsers.append('Safari')
                    elif 'Edge' in ua:
                        browsers.append('Edge')
                    else:
                        browsers.append('Other')
                
                browser_counts = pd.Series(browsers).value_counts()
                for browser, count in browser_counts.items():
                    user_analysis.append({
                        'Category': 'Browser',
                        'Value': browser,
                        'Count': count,
                        'Percentage': round((count / len(df)) * 100, 2)
                    })
            
            user_df = pd.DataFrame(user_analysis)
            user_df.to_excel(writer, sheet_name='User Analysis', index=False)
        
        # Sheet 4: Performance Analysis
        if not df.empty:
            performance_data = {
                'Metric': [
                    'Average Execution Time (seconds)',
                    'Median Execution Time (seconds)',
                    'Fastest Run (seconds)',
                    'Slowest Run (seconds)',
                    'Average Records Processed',
                    'Average Data Volume (bytes)',
                    'Average AI Calls per Run',
                    'Average BigQuery Queries per Run'
                ],
                'Value': [
                    round(df['execution_time'].mean(), 2) if 'execution_time' in df.columns else 0,
                    round(df['execution_time'].median(), 2) if 'execution_time' in df.columns else 0,
                    round(df['execution_time'].min(), 2) if 'execution_time' in df.columns else 0,
                    round(df['execution_time'].max(), 2) if 'execution_time' in df.columns else 0,
                    round(df['records_processed'].mean(), 0) if 'records_processed' in df.columns else 0,
                    round(df['data_volume_bytes'].mean(), 0) if 'data_volume_bytes' in df.columns else 0,
                    round(df['ai_calls'].mean(), 1) if 'ai_calls' in df.columns else 0,
                    round(df['bq_queries'].mean(), 1) if 'bq_queries' in df.columns else 0
                ]
            }
            perf_df = pd.DataFrame(performance_data)
            perf_df.to_excel(writer, sheet_name='Performance Analysis', index=False)
        
        # Sheet 5: Top Counties and Years
        if not df.empty:
            # County analysis
            all_counties = []
            for counties_str in df['counties'].dropna():
                counties = counties_str.split(';')
                all_counties.extend(counties)
            
            county_counts = pd.Series(all_counties).value_counts().head(20)
            county_data = []
            for county, count in county_counts.items():
                county_data.append({
                    'County': county,
                    'Usage Count': count,
                    'Percentage': round((count / len(all_counties)) * 100, 2)
                })
            
            county_df = pd.DataFrame(county_data)
            county_df.to_excel(writer, sheet_name='Top Counties', index=False)
            
            # Year analysis
            all_years = []
            for years_str in df['years'].dropna():
                years = years_str.split(';')
                all_years.extend([int(y) for y in years if y.isdigit()])
            
            year_counts = pd.Series(all_years).value_counts().sort_index()
            year_data = []
            for year, count in year_counts.items():
                year_data.append({
                    'Year': year,
                    'Usage Count': count,
                    'Percentage': round((count / len(all_years)) * 100, 2)
                })
            
            year_df = pd.DataFrame(year_data)
            year_df.to_excel(writer, sheet_name='Year Usage', index=False)
        
        # Sheet 6: Error Analysis
        if not df.empty and 'error_message' in df.columns:
            error_df = df[df['error_message'].notna() & (df['error_message'] != '')]
            if not error_df.empty:
                error_df[['timestamp', 'counties', 'years', 'error_message']].to_excel(
                    writer, sheet_name='Errors', index=False
                )
    
    print(f"✅ Detailed report generated: {output_file}")
    print(f"📊 Total runs analyzed: {len(df)}")
    print(f"💰 Total estimated cost: ${cost_summary['total_cost']:.4f}")
    print(f"🤖 AI cost: ${cost_summary['ai_cost']:.4f}")
    print(f"🗄️ BigQuery cost: ${cost_summary['bq_cost']:.4f}")


def generate_summary_report(output_file: str = None):
    """Generate a summary CSV report."""
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"fdic_analyzer_summary_{timestamp}.csv"
    
    df = run_logger.get_runs_summary()
    
    if df.empty:
        print("No runs found in the logs.")
        return
    
    # Select key columns for summary
    summary_columns = [
        'run_id', 'timestamp', 'interface_type', 'counties', 'years',
        'execution_time', 'records_processed', 'ai_calls', 'bq_queries',
        'ai_cost_estimate', 'bq_cost_estimate', 'total_cost_estimate',
        'success', 'error_message'
    ]
    
    available_columns = [col for col in summary_columns if col in df.columns]
    summary_df = df[available_columns]
    
    summary_df.to_csv(output_file, index=False)
    print(f"✅ Summary report generated: {output_file}")


def main():
    """Main function to generate reports."""
    parser = argparse.ArgumentParser(description='Generate FDIC Analyzer run reports')
    parser.add_argument('--output', '-o', help='Output file name')
    parser.add_argument('--summary', '-s', action='store_true', help='Generate summary CSV only')
    parser.add_argument('--detailed', '-d', action='store_true', help='Generate detailed Excel report')
    
    args = parser.parse_args()
    
    if args.summary:
        generate_summary_report(args.output)
    elif args.detailed:
        generate_detailed_report(args.output)
    else:
        # Generate both by default
        generate_detailed_report(args.output)
        if args.output:
            summary_file = args.output.replace('.xlsx', '_summary.csv')
        else:
            summary_file = None
        generate_summary_report(summary_file)


if __name__ == "__main__":
    main() 