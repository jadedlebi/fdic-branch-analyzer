#!/usr/bin/env python3
"""
BigQuery utilities for FDIC bank branch data analysis.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'config'))
from config import PROJECT_ID, get_bq_credentials

from google.cloud import bigquery
from google.oauth2 import service_account
from typing import List, Dict, Any
import pandas as pd

def get_bigquery_client():
    """Get BigQuery client using environment-based credentials."""
    try:
        if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
            # Local: use key file
            credentials = service_account.Credentials.from_service_account_file(
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
            )
            client = bigquery.Client(credentials=credentials, project=PROJECT_ID)
        else:
            # Cloud Run: use default service account
            client = bigquery.Client(project=PROJECT_ID)
        return client
    except Exception as e:
        print(f"Error creating BigQuery client: {e}")
        raise

def find_exact_county_match(county_input: str) -> list:
    """
    Find all possible county matches from the database.
    Args:
        county_input: County input in format "County, State" or "County State"
    Returns:
        List of possible county names from database (empty if none found)
    """
    try:
        client = get_bigquery_client()
        # Parse county and state
        if ',' in county_input:
            county_name, state = county_input.split(',', 1)
            county_name = county_name.strip()
            state = state.strip()
        else:
            parts = county_input.strip().split()
            if len(parts) >= 2:
                state = parts[-1]
                county_name = ' '.join(parts[:-1])
            else:
                county_name = county_input.strip()
                state = None
        # Build query to find matches
        if state:
            county_query = f"""
            SELECT DISTINCT county_state 
            FROM geo.cbsa_to_county 
            WHERE LOWER(county_state) LIKE LOWER('%{county_name}%')
            AND LOWER(county_state) LIKE LOWER('%{state}%')
            ORDER BY county_state
            """
        else:
            county_query = f"""
            SELECT DISTINCT county_state 
            FROM geo.cbsa_to_county 
            WHERE LOWER(county_state) LIKE LOWER('%{county_name}%')
            ORDER BY county_state
            """
        county_job = client.query(county_query)
        county_results = list(county_job.result())
        matches = [row.county_state for row in county_results]
        return matches
    except Exception as e:
        print(f"Error finding county match for {county_input}: {e}")
        return []

def execute_query(sql_template: str, county: str, year: int) -> List[Dict[str, Any]]:
    """
    Execute a BigQuery SQL query with parameter substitution.
    
    Args:
        sql_template: SQL query template with @county and @year parameters
        county: County name in "County, State" format
        year: Year as integer
        
    Returns:
        List of dictionaries containing query results
    """
    try:
        client = get_bigquery_client()
        
        # Find the exact county match from the database
        county_matches = find_exact_county_match(county)
        
        if not county_matches:
            raise Exception(f"No matching counties found for: {county}")
        
        # Use the first match (or the one selected by the user)
        exact_county = county_matches[0]
        
        # Substitute parameters in SQL template - ensure proper quoting
        sql = sql_template.replace('@county', f"'{exact_county}'").replace('@year', f"'{year}'")
        
        # Debug: print the SQL query to see what's being executed
        print(f"    Executing SQL: {sql[:200]}...")
        
        # Execute query
        query_job = client.query(sql)
        results = query_job.result()
        
        # Convert to list of dictionaries
        data = []
        for row in results:
            data.append(dict(row.items()))
        
        return data
        
    except Exception as e:
        raise Exception(f"Error executing BigQuery query for {county} {year}: {e}")

def test_connection() -> bool:
    """Test BigQuery connection and return True if successful."""
    try:
        client = get_bigquery_client()
        # Run a simple test query
        query = "SELECT 1 as test"
        query_job = client.query(query)
        query_job.result()
        return True
    except Exception as e:
        print(f"BigQuery connection test failed: {e}")
        return False

def get_available_counties() -> List[str]:
    """Get list of available counties from the database."""
    try:
        print("Getting BigQuery client...")
        client = get_bigquery_client()
        print("Client obtained:", client)
        query = """
        SELECT DISTINCT county_state 
        FROM geo.cbsa_to_county 
        ORDER BY county_state
        """
        print("Running query:", query)
        query_job = client.query(query)
        results = query_job.result()
        counties = [row.county_state for row in results]
        print("Counties fetched:", counties)
        return counties
    except Exception as e:
        print(f"Error getting available counties: {e}")
        return []

def get_available_years() -> List[int]:
    """Get list of available years from the database."""
    try:
        client = get_bigquery_client()
        query = """
        SELECT DISTINCT year 
        FROM branches.sod 
        ORDER BY year DESC
        """
        query_job = client.query(query)
        results = query_job.result()
        
        years = [row.year for row in results]
        return years
        
    except Exception as e:
        print(f"Error getting available years: {e}")
        return []