#!/usr/bin/env python3
"""
View and manage FDIC Analyzer run logs.
"""

import os
import sys
import argparse
import pandas as pd
from datetime import datetime

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.utils.run_logger import run_logger

def view_summary():
    """Display a summary of all runs."""
    df = run_logger.get_runs_summary()
    cost_summary = run_logger.get_cost_summary()
    
    if df.empty:
        print("📊 No runs found in the logs.")
        return
    
    print("📊 FDIC Analyzer Run Summary")
    print("=" * 50)
    print(f"Total Runs: {cost_summary['total_runs']}")
    print(f"Successful Runs: {cost_summary['successful_runs']}")
    print(f"Failed Runs: {cost_summary['total_runs'] - cost_summary['successful_runs']}")
    print(f"Success Rate: {(cost_summary['successful_runs'] / cost_summary['total_runs']) * 100:.1f}%")
    print()
    print("💰 Cost Summary")
    print("-" * 30)
    print(f"Total Cost: ${cost_summary['total_cost']:.4f}")
    print(f"AI Cost: ${cost_summary['ai_cost']:.4f}")
    print(f"BigQuery Cost: ${cost_summary['bq_cost']:.4f}")
    print(f"Average Cost per Run: ${cost_summary['avg_cost_per_run']:.4f}")
    print()
    
    if not df.empty:
        print("📈 Recent Runs")
        print("-" * 30)
        recent_runs = df.tail(5)
        for _, run in recent_runs.iterrows():
            timestamp = pd.to_datetime(run['timestamp']).strftime('%Y-%m-%d %H:%M')
            counties = run['counties'].split(';')[:2]  # Show first 2 counties
            counties_str = ', '.join(counties) + ('...' if len(run['counties'].split(';')) > 2 else '')
            status = "✅" if run['success'] else "❌"
            cost = f"${run['total_cost_estimate']:.4f}"
            print(f"{status} {timestamp} | {counties_str} | {cost}")


def view_detailed_run(run_id):
    """Display detailed information for a specific run."""
    details = run_logger.get_run_details(run_id)
    
    if not details:
        print(f"❌ Run {run_id} not found.")
        return
    
    print(f"📋 Detailed Run Information: {run_id}")
    print("=" * 60)
    print(f"Timestamp: {details['timestamp']}")
    print(f"Interface: {details['interface_type']}")
    print(f"User IP: {details.get('user_ip', 'N/A')}")
    print(f"Session ID: {details.get('session_id', 'N/A')}")
    print()
    print(f"Counties: {', '.join(details['counties'])}")
    print(f"Years: {', '.join(map(str, details['years']))}")
    print()
    print(f"Execution Time: {details.get('execution_time', 0):.2f} seconds")
    print(f"Records Processed: {details.get('records_processed', 0)}")
    print()
    print("🤖 AI Usage")
    print("-" * 20)
    print(f"Provider: {details.get('ai_provider', 'N/A')}")
    print(f"Model: {details.get('ai_model', 'N/A')}")
    print(f"Calls: {details.get('ai_calls', 0)}")
    print(f"Input Tokens: {details.get('ai_input_tokens', 0)}")
    print(f"Output Tokens: {details.get('ai_output_tokens', 0)}")
    print(f"AI Cost: ${details.get('ai_cost_estimate', 0):.4f}")
    print()
    print("🗄️ BigQuery Usage")
    print("-" * 20)
    print(f"Queries: {details.get('bq_queries', 0)}")
    print(f"Bytes Processed: {details.get('bq_bytes_processed', 0):,}")
    print(f"BigQuery Cost: ${details.get('bq_cost_estimate', 0):.4f}")
    print()
    print(f"Total Cost: ${details.get('total_cost_estimate', 0):.4f}")
    print(f"Success: {'✅' if details.get('success') else '❌'}")
    if details.get('error_message'):
        print(f"Error: {details['error_message']}")
    print()
    print("📁 Generated Files")
    print("-" * 20)
    if details.get('excel_file'):
        print(f"Excel: {details['excel_file']}")
    if details.get('pdf_file'):
        print(f"PDF: {details['pdf_file']}")


def list_runs(limit=10):
    """List recent runs with basic information."""
    df = run_logger.get_runs_summary()
    
    if df.empty:
        print("📊 No runs found in the logs.")
        return
    
    print("📊 Recent Runs")
    print("=" * 80)
    print(f"{'Run ID':<36} {'Timestamp':<20} {'Interface':<6} {'Counties':<20} {'Cost':<10} {'Status'}")
    print("-" * 80)
    
    recent_runs = df.tail(limit)
    for _, run in recent_runs.iterrows():
        run_id = run['run_id'][:35] + "..." if len(run['run_id']) > 35 else run['run_id']
        timestamp = pd.to_datetime(run['timestamp']).strftime('%Y-%m-%d %H:%M')
        interface = run['interface_type']
        counties = run['counties'].split(';')[:1]  # Show first county only
        counties_str = counties[0] if counties else 'N/A'
        if len(counties_str) > 18:
            counties_str = counties_str[:15] + "..."
        cost = f"${run['total_cost_estimate']:.4f}"
        status = "✅" if run['success'] else "❌"
        
        print(f"{run_id:<36} {timestamp:<20} {interface:<6} {counties_str:<20} {cost:<10} {status}")


def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(description='View FDIC Analyzer run logs')
    parser.add_argument('--summary', '-s', action='store_true', help='Show summary of all runs')
    parser.add_argument('--list', '-l', action='store_true', help='List recent runs')
    parser.add_argument('--detailed', '-d', help='Show detailed information for a specific run ID')
    parser.add_argument('--limit', type=int, default=10, help='Number of runs to list (default: 10)')
    parser.add_argument('--generate-report', '-r', action='store_true', help='Generate Excel report of all runs')
    parser.add_argument('--output', '-o', help='Output file for generated report')
    
    args = parser.parse_args()
    
    if args.summary:
        view_summary()
    elif args.list:
        list_runs(args.limit)
    elif args.detailed:
        view_detailed_run(args.detailed)
    elif args.generate_report:
        from scripts.generate_run_report import generate_detailed_report
        generate_detailed_report(args.output)
    else:
        # Default: show summary
        view_summary()


if __name__ == "__main__":
    main() 