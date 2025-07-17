#!/usr/bin/env python3
"""
BigQuery wrapper that tracks query usage and costs for logging.
"""

import sys
import os
from typing import List, Dict, Any
import json

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils.bq_utils import get_bigquery_client, find_exact_county_match
from src.utils.run_logger import run_logger
from google.cloud import bigquery

class TrackedBigQueryClient:
    """BigQuery client wrapper that tracks usage for logging."""
    
    def __init__(self, run_id: str):
        """Initialize the tracked BigQuery client."""
        self.run_id = run_id
        self.client = get_bigquery_client()
        self.total_queries = 0
        self.total_bytes_processed = 0
        
    def execute_query(self, sql_template: str, county: str, year: int) -> List[Dict[str, Any]]:
        """Execute a BigQuery query and track usage."""
        try:
            # Find the exact county match
            county_matches = find_exact_county_match(county)
            
            if not county_matches:
                raise Exception(f"No matching counties found for: {county}")
            
            exact_county = county_matches[0]
            
            # Substitute parameters in SQL template
            sql = sql_template.replace('@county', f"'{exact_county}'").replace('@year', f"'{year}'")
            
            # Execute query
            query_job = self.client.query(sql)
            results = query_job.result()
            
            # Get query statistics
            total_bytes_processed = query_job.total_bytes_processed or 0
            
            # Convert to list of dictionaries
            data = []
            for row in results:
                data.append(dict(row.items()))
            
            # Update tracking
            self.total_queries += 1
            self.total_bytes_processed += total_bytes_processed
            
            # Update run metadata
            run_logger.update_run(
                self.run_id,
                bq_queries=self.total_queries,
                bq_bytes_processed=self.total_bytes_processed,
                records_processed=len(data)
            )
            
            return data
            
        except Exception as e:
            raise Exception(f"Error executing BigQuery query for {county} {year}: {e}")
    
    def get_query_stats(self) -> Dict[str, Any]:
        """Get current query statistics."""
        return {
            'total_queries': self.total_queries,
            'total_bytes_processed': self.total_bytes_processed,
            'estimated_cost': (self.total_bytes_processed / (1024**4)) * 5.0  # $5 per TB
        }


def track_bq_query(run_id: str, sql: str, county: str, year: int) -> List[Dict[str, Any]]:
    """Track a single BigQuery query for logging purposes."""
    try:
        client = TrackedBigQueryClient(run_id)
        return client.execute_query(sql, county, year)
        
    except Exception as e:
        print(f"Error in tracked BigQuery query: {e}")
        return [] 