#!/usr/bin/env python3
"""
Configuration settings for the AI-assisted FDIC bank branch report generator.
"""

import os
import json

# Base directory paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, 'docs')
DATA_DIR = os.path.join(BASE_DIR, 'data')
CREDENTIALS_DIR = os.path.join(BASE_DIR, 'credentials')

# File paths
PROMPT_PATH = os.path.join(DOCS_DIR, 'prompts', 'reporting_prompt.txt')
SQL_TEMPLATE_PATH = os.path.join(DOCS_DIR, 'query_templates', 'branch_report.sql')
OUTPUT_DIR = os.path.join(DATA_DIR, 'reports')

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# AI Configuration
AI_PROVIDER = "claude"  # Options: "gpt-4", "claude"
CLAUDE_MODEL = "claude-3-5-sonnet-20241022"
GPT_MODEL = "gpt-4"

# BigQuery Configuration
PROJECT_ID = "hdma1-242116"
DATASET_ID = "branches"
TABLE_ID = "sod"

# Report Configuration
DEFAULT_YEARS = list(range(2017, 2025))  # 2017-2024
MAX_BANKS_DISPLAY = 10

# Load environment variables from .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not found. Make sure API keys are set in environment.")

# BigQuery credentials from environment variables
def get_bq_credentials():
    """Get BigQuery credentials from environment variables."""
    credentials = {
        "type": os.getenv("BQ_TYPE"),
        "project_id": os.getenv("BQ_PROJECT_ID"),
        "private_key_id": os.getenv("BQ_PRIVATE_KEY_ID"),
        "private_key": os.getenv("BQ_PRIVATE_KEY"),
        "client_email": os.getenv("BQ_CLIENT_EMAIL"),
        "client_id": os.getenv("BQ_CLIENT_ID"),
        "auth_uri": os.getenv("BQ_AUTH_URI"),
        "token_uri": os.getenv("BQ_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("BQ_AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.getenv("BQ_CLIENT_X509_CERT_URL")
    }
    
    # Validate that all required fields are present
    required_fields = ["type", "project_id", "private_key", "client_email"]
    missing_fields = [field for field in required_fields if not credentials.get(field)]
    
    if missing_fields:
        raise ValueError(f"Missing required BigQuery credentials in environment: {missing_fields}")
    
    return credentials

# Load API keys based on provider
if AI_PROVIDER == "openai":
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        print("Warning: OPENAI_API_KEY not found in environment variables.")
elif AI_PROVIDER == "claude":
    CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
    if not CLAUDE_API_KEY:
        print("Warning: CLAUDE_API_KEY not found in environment variables.")
else:
    print(f"Warning: Unknown AI provider '{AI_PROVIDER}'. Please set to 'openai' or 'claude'.")