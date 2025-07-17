#!/usr/bin/env python3
"""
Query cost details from BigQuery ai_logs table.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Set up Google Cloud credentials
try:
    from scripts.setup_gcp_credentials import setup_environment
    setup_environment()
except ImportError:
    print("Warning: Could not set up GCP credentials")

from google.cloud import bigquery

def query_cost_details():
    """Query the most recent run's cost details."""
    try:
        client = bigquery.Client()
        
        query = """
        SELECT 
            run_id,
            total_cost_estimate,
            ai_cost_estimate,
            bq_cost_estimate,
            ai_input_tokens,
            ai_output_tokens,
            bq_bytes_processed,
            ai_provider,
            ai_model,
            ai_calls,
            bq_queries
        FROM `hdma1-242116.branches.ai_logs`
        ORDER BY timestamp DESC
        LIMIT 1
        """
        
        results = list(client.query(query).result())
        
        if not results:
            print("❌ No logs found in BigQuery table.")
            return
        
        row = results[0]
        
        print("📊 Cost Breakdown for Most Recent Run:")
        print("=" * 50)
        print(f"Run ID: {row.run_id}")
        print(f"Total Cost: ${row.total_cost_estimate:.6f}")
        print()
        print("🤖 AI Usage:")
        print(f"  Provider: {row.ai_provider}")
        print(f"  Model: {row.ai_model}")
        print(f"  Calls: {row.ai_calls}")
        print(f"  Input Tokens: {row.ai_input_tokens:,}")
        print(f"  Output Tokens: {row.ai_output_tokens:,}")
        print(f"  AI Cost: ${row.ai_cost_estimate:.6f}")
        print()
        print("🗄️ BigQuery Usage:")
        print(f"  Queries: {row.bq_queries}")
        print(f"  Bytes Processed: {row.bq_bytes_processed:,}")
        print(f"  BigQuery Cost: ${row.bq_cost_estimate:.6f}")
        print()
        print("💰 Cost Analysis:")
        print(f"  AI Cost %: {(row.ai_cost_estimate / row.total_cost_estimate * 100):.1f}%")
        print(f"  BigQuery Cost %: {(row.bq_cost_estimate / row.total_cost_estimate * 100):.1f}%")
        
    except Exception as e:
        print(f"❌ Error accessing BigQuery: {e}")

if __name__ == "__main__":
    query_cost_details() 