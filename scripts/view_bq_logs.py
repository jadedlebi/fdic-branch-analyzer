#!/usr/bin/env python3
"""
View logs from BigQuery ai_logs table.
"""

import sys
import os
from datetime import datetime, timedelta

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Set up Google Cloud credentials
try:
    from scripts.setup_gcp_credentials import setup_environment
    setup_environment()
except ImportError:
    print("Warning: Could not set up GCP credentials")

from google.cloud import bigquery

def view_bq_logs(limit=10):
    """View recent logs from BigQuery ai_logs table."""
    try:
        client = bigquery.Client()
        
        # Query to get recent logs
        query = f"""
        SELECT 
            run_id,
            timestamp,
            interface_type,
            counties,
            years,
            execution_time,
            records_processed,
            ai_calls,
            bq_queries,
            ai_cost_estimate,
            bq_cost_estimate,
            total_cost_estimate,
            success,
            error_message
        FROM `hdma1-242116.branches.ai_logs`
        ORDER BY timestamp DESC
        LIMIT {limit}
        """
        
        print(f"📊 Fetching last {limit} runs from BigQuery...")
        print("=" * 80)
        
        query_job = client.query(query)
        results = query_job.result()
        
        if not results:
            print("❌ No logs found in BigQuery table.")
            return
        
        print(f"{'Run ID':<36} {'Timestamp':<20} {'Interface':<8} {'Counties':<20} {'Cost':<10} {'Status'}")
        print("-" * 80)
        
        for row in results:
            run_id = row.run_id[:35] + "..." if len(row.run_id) > 35 else row.run_id
            timestamp = row.timestamp.strftime('%Y-%m-%d %H:%M') if row.timestamp else 'N/A'
            interface = row.interface_type or 'N/A'
            
            # Get first county for display
            counties = row.counties.split(';')[:1] if row.counties else []
            counties_str = counties[0] if counties else 'N/A'
            if len(counties_str) > 18:
                counties_str = counties_str[:15] + "..."
            
            cost = f"${row.total_cost_estimate:.4f}" if row.total_cost_estimate else '$0.0000'
            status = "✅" if row.success else "❌"
            
            print(f"{run_id:<36} {timestamp:<20} {interface:<8} {counties_str:<20} {cost:<10} {status}")
        
        print("\n" + "=" * 80)
        
        # Get summary statistics
        summary_query = """
        SELECT 
            COUNT(*) as total_runs,
            COUNTIF(success = true) as successful_runs,
            SUM(total_cost_estimate) as total_cost,
            SUM(ai_cost_estimate) as ai_cost,
            SUM(bq_cost_estimate) as bq_cost,
            AVG(execution_time) as avg_execution_time
        FROM `hdma1-242116.branches.ai_logs`
        """
        
        summary_job = client.query(summary_query)
        summary_result = list(summary_job.result())[0]
        
        print("📈 Summary Statistics:")
        print(f"   Total Runs: {summary_result.total_runs}")
        print(f"   Successful Runs: {summary_result.successful_runs}")
        print(f"   Success Rate: {(summary_result.successful_runs / summary_result.total_runs * 100):.1f}%")
        print(f"   Total Cost: ${summary_result.total_cost:.4f}")
        print(f"   AI Cost: ${summary_result.ai_cost:.4f}")
        print(f"   BigQuery Cost: ${summary_result.bq_cost:.4f}")
        print(f"   Avg Execution Time: {summary_result.avg_execution_time:.2f}s")
        
    except Exception as e:
        print(f"❌ Error accessing BigQuery: {e}")

def view_detailed_run(run_id):
    """View detailed information for a specific run from BigQuery."""
    try:
        client = bigquery.Client()
        
        query = f"""
        SELECT *
        FROM `hdma1-242116.branches.ai_logs`
        WHERE run_id = '{run_id}'
        LIMIT 1
        """
        
        query_job = client.query(query)
        results = list(query_job.result())
        
        if not results:
            print(f"❌ Run {run_id} not found in BigQuery.")
            return
        
        row = results[0]
        
        print(f"📋 Detailed Run Information: {run_id}")
        print("=" * 60)
        print(f"Timestamp: {row.timestamp}")
        print(f"Interface: {row.interface_type}")
        print(f"User IP: {row.user_ip or 'N/A'}")
        print(f"Session ID: {row.session_id or 'N/A'}")
        print()
        print(f"Counties: {row.counties}")
        print(f"Years: {row.years}")
        print()
        print(f"Execution Time: {row.execution_time:.2f} seconds")
        print(f"Records Processed: {row.records_processed}")
        print()
        print("🤖 AI Usage")
        print("-" * 20)
        print(f"Provider: {row.ai_provider or 'N/A'}")
        print(f"Model: {row.ai_model or 'N/A'}")
        print(f"Calls: {row.ai_calls}")
        print(f"Input Tokens: {row.ai_input_tokens}")
        print(f"Output Tokens: {row.ai_output_tokens}")
        print(f"AI Cost: ${row.ai_cost_estimate:.4f}")
        print()
        print("🗄️ BigQuery Usage")
        print("-" * 20)
        print(f"Queries: {row.bq_queries}")
        print(f"Bytes Processed: {row.bq_bytes_processed:,}")
        print(f"BigQuery Cost: ${row.bq_cost_estimate:.4f}")
        print()
        print(f"Total Cost: ${row.total_cost_estimate:.4f}")
        print(f"Success: {'✅' if row.success else '❌'}")
        if row.error_message:
            print(f"Error: {row.error_message}")
        print()
        print("📁 Generated Files")
        print("-" * 20)
        if row.excel_file:
            print(f"Excel: {row.excel_file}")
        if row.pdf_file:
            print(f"PDF: {row.pdf_file}")
        
    except Exception as e:
        print(f"❌ Error accessing BigQuery: {e}")

def main():
    """Main function to handle command line arguments."""
    import argparse
    
    parser = argparse.ArgumentParser(description='View BigQuery logs')
    parser.add_argument('--limit', '-l', type=int, default=10, help='Number of runs to show (default: 10)')
    parser.add_argument('--detailed', '-d', help='Show detailed information for a specific run ID')
    
    args = parser.parse_args()
    
    if args.detailed:
        view_detailed_run(args.detailed)
    else:
        view_bq_logs(args.limit)

if __name__ == "__main__":
    main() 