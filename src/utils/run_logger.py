#!/usr/bin/env python3
"""
Run logging and tracking system for FDIC Branch Analyzer.
Tracks costs, queries, user information, and performance metrics.
"""

import os
import json
import csv
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import pandas as pd
from dataclasses import dataclass, asdict
import requests
from user_agents import parse
from google.cloud import bigquery

# Import configuration
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'config'))
from config import DATA_DIR

# Cost estimates (in USD per 1K tokens)
COST_ESTIMATES = {
    "claude": {
        "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015},
        "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet-20240229": {"input": 0.003, "output": 0.015},
        "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125}
    },
    "openai": {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002}
    }
}

# BigQuery cost estimate (per TB processed)
BQ_COST_PER_TB = 5.0  # USD per TB

BQ_LOG_DATASET = "branches"
BQ_LOG_TABLE = "ai_logs"

@dataclass
class RunMetadata:
    """Metadata for a single run of the tool."""
    run_id: str
    timestamp: str
    user_ip: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    interface_type: str = "web"  # "web" or "cli"
    
    # Query parameters
    counties: List[str] = None
    years: List[int] = None
    
    # Performance metrics
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    execution_time: Optional[float] = None
    
    # Data metrics
    records_processed: int = 0
    data_volume_bytes: int = 0
    
    # AI usage
    ai_provider: Optional[str] = None
    ai_model: Optional[str] = None
    ai_calls: int = 0
    ai_input_tokens: int = 0
    ai_output_tokens: int = 0
    ai_cost_estimate: float = 0.0
    
    # BigQuery usage
    bq_queries: int = 0
    bq_bytes_processed: int = 0
    bq_cost_estimate: float = 0.0
    
    # Total cost
    total_cost_estimate: float = 0.0
    
    # Success/failure
    success: bool = False
    error_message: Optional[str] = None
    
    # Generated files
    excel_file: Optional[str] = None
    pdf_file: Optional[str] = None
    
    def __post_init__(self):
        if self.counties is None:
            self.counties = []
        if self.years is None:
            self.years = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    def calculate_costs(self):
        """Calculate cost estimates for AI and BigQuery usage."""
        # Calculate AI costs
        if self.ai_provider and self.ai_model:
            provider_costs = COST_ESTIMATES.get(self.ai_provider, {})
            model_costs = provider_costs.get(self.ai_model, {"input": 0, "output": 0})
            
            input_cost = (self.ai_input_tokens / 1000) * model_costs["input"]
            output_cost = (self.ai_output_tokens / 1000) * model_costs["output"]
            self.ai_cost_estimate = input_cost + output_cost
        
        # Calculate BigQuery costs
        if self.bq_bytes_processed > 0:
            tb_processed = self.bq_bytes_processed / (1024**4)  # Convert to TB
            self.bq_cost_estimate = tb_processed * BQ_COST_PER_TB
        
        # Calculate total cost
        self.total_cost_estimate = self.ai_cost_estimate + self.bq_cost_estimate
    
    def finalize(self):
        """Finalize the run metadata with timing and cost calculations."""
        if self.start_time and self.end_time:
            self.execution_time = self.end_time - self.start_time
        
        self.calculate_costs()


class RunLogger:
    """Main logging class for tracking tool runs."""
    
    def __init__(self, log_dir: Optional[str] = None):
        """Initialize the run logger."""
        if log_dir is None:
            log_dir = os.path.join(DATA_DIR, 'logs')
        
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        
        # File paths
        self.runs_file = os.path.join(self.log_dir, 'runs.csv')
        self.detailed_logs_dir = os.path.join(self.log_dir, 'detailed')
        os.makedirs(self.detailed_logs_dir, exist_ok=True)
        
        # Initialize CSV file if it doesn't exist
        self._init_csv_file()
    
    def _init_csv_file(self):
        """Initialize the CSV file with headers if it doesn't exist."""
        if not os.path.exists(self.runs_file):
            with open(self.runs_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'run_id', 'timestamp', 'user_ip', 'user_agent', 'session_id',
                    'interface_type', 'counties', 'years', 'start_time', 'end_time',
                    'execution_time', 'records_processed', 'data_volume_bytes',
                    'ai_provider', 'ai_model', 'ai_calls', 'ai_input_tokens',
                    'ai_output_tokens', 'ai_cost_estimate', 'bq_queries',
                    'bq_bytes_processed', 'bq_cost_estimate', 'total_cost_estimate',
                    'success', 'error_message', 'excel_file', 'pdf_file'
                ])
    
    def start_run(self, 
                  counties: List[str], 
                  years: List[int], 
                  interface_type: str = "web",
                  user_ip: Optional[str] = None,
                  user_agent: Optional[str] = None,
                  session_id: Optional[str] = None) -> str:
        """Start tracking a new run and return the run ID."""
        run_id = str(uuid.uuid4())
        
        metadata = RunMetadata(
            run_id=run_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            user_ip=user_ip,
            user_agent=user_agent,
            session_id=session_id,
            interface_type=interface_type,
            counties=counties,
            years=years,
            start_time=time.time()
        )
        
        # Save detailed log
        detailed_file = os.path.join(self.detailed_logs_dir, f"{run_id}.json")
        with open(detailed_file, 'w') as f:
            json.dump(metadata.to_dict(), f, indent=2)
        
        return run_id
    
    def update_run(self, run_id: str, **kwargs):
        """Update run metadata with new information."""
        detailed_file = os.path.join(self.detailed_logs_dir, f"{run_id}.json")
        
        if os.path.exists(detailed_file):
            with open(detailed_file, 'r') as f:
                data = json.load(f)
            
            # Update with new data
            data.update(kwargs)
            
            with open(detailed_file, 'w') as f:
                json.dump(data, f, indent=2)
    
    def upload_run_to_bigquery(self, run_data: dict):
        """
        Upload a single run's data to BigQuery (branches.ai_logs).
        Table is created if it does not exist. Table is private by default (do not share with public).
        """
        try:
            client = bigquery.Client()
            dataset_ref = client.dataset(BQ_LOG_DATASET)
            table_ref = dataset_ref.table(BQ_LOG_TABLE)

            # Define schema (update as needed for new fields)
            schema = [
                bigquery.SchemaField("run_id", "STRING"),
                bigquery.SchemaField("timestamp", "TIMESTAMP"),
                bigquery.SchemaField("user_ip", "STRING"),
                bigquery.SchemaField("user_agent", "STRING"),
                bigquery.SchemaField("session_id", "STRING"),
                bigquery.SchemaField("interface_type", "STRING"),
                bigquery.SchemaField("counties", "STRING"),
                bigquery.SchemaField("years", "STRING"),
                bigquery.SchemaField("start_time", "FLOAT64"),
                bigquery.SchemaField("end_time", "FLOAT64"),
                bigquery.SchemaField("execution_time", "FLOAT64"),
                bigquery.SchemaField("records_processed", "INTEGER"),
                bigquery.SchemaField("data_volume_bytes", "INTEGER"),
                bigquery.SchemaField("ai_provider", "STRING"),
                bigquery.SchemaField("ai_model", "STRING"),
                bigquery.SchemaField("ai_calls", "INTEGER"),
                bigquery.SchemaField("ai_input_tokens", "INTEGER"),
                bigquery.SchemaField("ai_output_tokens", "INTEGER"),
                bigquery.SchemaField("ai_cost_estimate", "FLOAT64"),
                bigquery.SchemaField("bq_queries", "INTEGER"),
                bigquery.SchemaField("bq_bytes_processed", "INTEGER"),
                bigquery.SchemaField("bq_cost_estimate", "FLOAT64"),
                bigquery.SchemaField("total_cost_estimate", "FLOAT64"),
                bigquery.SchemaField("success", "BOOL"),
                bigquery.SchemaField("error_message", "STRING"),
                bigquery.SchemaField("excel_file", "STRING"),
                bigquery.SchemaField("pdf_file", "STRING"),
            ]

            # Create table if it doesn't exist
            try:
                client.get_table(table_ref)
            except Exception:
                table = bigquery.Table(table_ref, schema=schema)
                table = client.create_table(table)
                # Table is private by default; do not grant public access

            # Prepare row for insertion
            row = run_data.copy()
            # Convert lists to strings for BigQuery
            row["counties"] = ";".join(row.get("counties", [])) if isinstance(row.get("counties"), list) else row.get("counties", "")
            row["years"] = ";".join(map(str, row.get("years", []))) if isinstance(row.get("years"), list) else row.get("years", "")
            # Convert timestamps to ISO format if needed
            if isinstance(row.get("timestamp"), (str, type(None))):
                pass
            else:
                row["timestamp"] = row["timestamp"].isoformat()
            # Insert row
            errors = client.insert_rows_json(table_ref, [row])
            if errors:
                print(f"[BigQuery Log] Error uploading run: {errors}")
            else:
                print(f"[BigQuery Log] Run uploaded to {BQ_LOG_DATASET}.{BQ_LOG_TABLE}")
        except Exception as e:
            print(f"[BigQuery Log] Exception: {e}")

    def end_run(self, run_id: str, success: bool = True, error_message: Optional[str] = None):
        """End a run and finalize the metadata."""
        detailed_file = os.path.join(self.detailed_logs_dir, f"{run_id}.json")
        
        if os.path.exists(detailed_file):
            with open(detailed_file, 'r') as f:
                data = json.load(f)
            
            # Update final data
            data['end_time'] = time.time()
            data['success'] = success
            if error_message:
                data['error_message'] = error_message
            
            # Calculate execution time
            if data.get('start_time') and data.get('end_time'):
                data['execution_time'] = data['end_time'] - data['start_time']
            
            # Calculate costs
            self._calculate_costs(data)
            
            # Save updated data
            with open(detailed_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Add to CSV summary
            self._add_to_csv(data)

            # Upload to BigQuery (privacy: table is private by default)
            self.upload_run_to_bigquery(data)
    
    def _calculate_costs(self, data: Dict[str, Any]):
        """Calculate cost estimates for a run."""
        # AI costs
        ai_provider = data.get('ai_provider')
        ai_model = data.get('ai_model')
        if ai_provider and ai_model:
            provider_costs = COST_ESTIMATES.get(ai_provider, {})
            model_costs = provider_costs.get(ai_model, {"input": 0, "output": 0})
            
            input_tokens = data.get('ai_input_tokens', 0)
            output_tokens = data.get('ai_output_tokens', 0)
            
            input_cost = (input_tokens / 1000) * model_costs["input"]
            output_cost = (output_tokens / 1000) * model_costs["output"]
            data['ai_cost_estimate'] = input_cost + output_cost
        
        # BigQuery costs
        bq_bytes = data.get('bq_bytes_processed', 0)
        if bq_bytes > 0:
            tb_processed = bq_bytes / (1024**4)  # Convert to TB
            data['bq_cost_estimate'] = tb_processed * BQ_COST_PER_TB
        
        # Total cost
        data['total_cost_estimate'] = data.get('ai_cost_estimate', 0) + data.get('bq_cost_estimate', 0)
    
    def _add_to_csv(self, data: Dict[str, Any]):
        """Add run data to the CSV summary file."""
        with open(self.runs_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                data.get('run_id', ''),
                data.get('timestamp', ''),
                data.get('user_ip', ''),
                data.get('user_agent', ''),
                data.get('session_id', ''),
                data.get('interface_type', ''),
                ';'.join(data.get('counties', [])),
                ';'.join(map(str, data.get('years', []))),
                data.get('start_time', ''),
                data.get('end_time', ''),
                data.get('execution_time', ''),
                data.get('records_processed', 0),
                data.get('data_volume_bytes', 0),
                data.get('ai_provider', ''),
                data.get('ai_model', ''),
                data.get('ai_calls', 0),
                data.get('ai_input_tokens', 0),
                data.get('ai_output_tokens', 0),
                data.get('ai_cost_estimate', 0.0),
                data.get('bq_queries', 0),
                data.get('bq_bytes_processed', 0),
                data.get('bq_cost_estimate', 0.0),
                data.get('total_cost_estimate', 0.0),
                data.get('success', False),
                data.get('error_message', ''),
                data.get('excel_file', ''),
                data.get('pdf_file', '')
            ])
    
    def get_runs_summary(self) -> pd.DataFrame:
        """Get a summary of all runs as a pandas DataFrame."""
        if os.path.exists(self.runs_file):
            df = pd.read_csv(self.runs_file)
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        else:
            return pd.DataFrame()
    
    def get_run_details(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific run."""
        detailed_file = os.path.join(self.detailed_logs_dir, f"{run_id}.json")
        if os.path.exists(detailed_file):
            with open(detailed_file, 'r') as f:
                return json.load(f)
        return None
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """Get a summary of costs across all runs."""
        df = self.get_runs_summary()
        if df.empty:
            return {
                'total_runs': 0,
                'successful_runs': 0,
                'total_cost': 0.0,
                'ai_cost': 0.0,
                'bq_cost': 0.0,
                'avg_cost_per_run': 0.0
            }
        
        return {
            'total_runs': len(df),
            'successful_runs': len(df[df['success'] == True]),
            'total_cost': df['total_cost_estimate'].sum(),
            'ai_cost': df['ai_cost_estimate'].sum(),
            'bq_cost': df['bq_cost_estimate'].sum(),
            'avg_cost_per_run': df['total_cost_estimate'].mean()
        }
    
    def export_summary_report(self, output_file: str):
        """Export a comprehensive summary report."""
        df = self.get_runs_summary()
        cost_summary = self.get_cost_summary()
        
        # Convert DataFrame to records, handling Timestamp serialization
        if not df.empty:
            runs_data = []
            for _, row in df.iterrows():
                run_dict = {}
                for col, value in row.items():
                    if pd.isna(value):
                        run_dict[col] = None
                    elif isinstance(value, pd.Timestamp):
                        run_dict[col] = value.isoformat()
                    else:
                        run_dict[col] = value
                runs_data.append(run_dict)
        else:
            runs_data = []
        
        report = {
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'cost_summary': cost_summary,
            'runs_data': runs_data
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)


def get_user_info(request) -> Dict[str, Any]:
    """Extract user information from a Flask request."""
    user_info = {}
    
    # Get IP address
    if request.headers.get('X-Forwarded-For'):
        user_info['ip'] = request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        user_info['ip'] = request.headers.get('X-Real-IP')
    else:
        user_info['ip'] = request.remote_addr
    
    # Get user agent
    user_agent_string = request.headers.get('User-Agent', '')
    user_info['user_agent'] = user_agent_string
    
    # Parse user agent for additional info
    if user_agent_string:
        try:
            ua = parse(user_agent_string)
            user_info['browser'] = f"{ua.browser.family} {ua.browser.version_string}"
            user_info['os'] = f"{ua.os.family} {ua.os.version_string}"
            user_info['device'] = ua.device.family
        except:
            pass
    
    return user_info


# Global logger instance
run_logger = RunLogger() 