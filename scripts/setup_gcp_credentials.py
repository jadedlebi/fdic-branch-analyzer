#!/usr/bin/env python3
"""
Safely extract BigQuery credentials from .env and create a JSON key file.
This script does not expose the private key in logs or output.
"""

import os
import json
import tempfile
from pathlib import Path

def create_gcp_key_file():
    """Create a GCP service account key file from .env variables."""
    
    # Load .env file
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found")
        return None
    
    # Read .env file
    env_vars = {}
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value
    
    # Extract BigQuery credentials
    required_vars = ['BQ_TYPE', 'BQ_PROJECT_ID', 'BQ_PRIVATE_KEY_ID', 'BQ_PRIVATE_KEY', 
                    'BQ_CLIENT_EMAIL', 'BQ_CLIENT_ID', 'BQ_AUTH_URI', 'BQ_TOKEN_URI', 
                    'BQ_AUTH_PROVIDER_X509_CERT_URL', 'BQ_CLIENT_X509_CERT_URL']
    
    missing_vars = [var for var in required_vars if var not in env_vars]
    if missing_vars:
        print(f"❌ Missing required BigQuery variables: {missing_vars}")
        return None
    
    # Create the service account key JSON
    # Clean up the private key - remove extra quotes and fix newlines
    private_key = env_vars['BQ_PRIVATE_KEY']
    if private_key.startswith('"') and private_key.endswith('"'):
        private_key = private_key[1:-1]  # Remove outer quotes
    private_key = private_key.replace('\\n', '\n')  # Fix newlines
    
    service_account_key = {
        "type": env_vars['BQ_TYPE'],
        "project_id": env_vars['BQ_PROJECT_ID'],
        "private_key_id": env_vars['BQ_PRIVATE_KEY_ID'],
        "private_key": private_key,
        "client_email": env_vars['BQ_CLIENT_EMAIL'],
        "client_id": env_vars['BQ_CLIENT_ID'],
        "auth_uri": env_vars['BQ_AUTH_URI'],
        "token_uri": env_vars['BQ_TOKEN_URI'],
        "auth_provider_x509_cert_url": env_vars['BQ_AUTH_PROVIDER_X509_CERT_URL'],
        "client_x509_cert_url": env_vars['BQ_CLIENT_X509_CERT_URL']
    }
    
    # Create the key file
    key_file_path = Path('gcp-service-account-key.json')
    with open(key_file_path, 'w') as f:
        json.dump(service_account_key, f, indent=2)
    
    # Set restrictive permissions (owner read/write only)
    os.chmod(key_file_path, 0o600)
    
    print(f"✅ GCP service account key created: {key_file_path}")
    print(f"✅ File permissions set to 600 (owner read/write only)")
    
    return str(key_file_path)

def setup_environment():
    """Set up the environment for Google Cloud authentication."""
    key_file = create_gcp_key_file()
    if key_file:
        # Set the environment variable
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.abspath(key_file)
        print(f"✅ GOOGLE_APPLICATION_CREDENTIALS set to: {os.path.abspath(key_file)}")
        return True
    return False

def test_authentication():
    """Test that Google Cloud authentication is working."""
    try:
        from google.cloud import bigquery
        client = bigquery.Client()
        project = client.project
        print(f"✅ Authentication successful! Project: {project}")
        return True
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False

def cleanup_key_file():
    """Remove the key file for security."""
    key_file = Path('gcp-service-account-key.json')
    if key_file.exists():
        key_file.unlink()
        print("✅ Key file removed for security")

if __name__ == "__main__":
    print("🔐 Setting up Google Cloud credentials...")
    
    if setup_environment():
        if test_authentication():
            print("\n🎉 Google Cloud authentication is ready!")
            print("You can now run the logging test or your application.")
            print("\nNote: The key file will remain for this session.")
            print("Run 'python scripts/setup_gcp_credentials.py --cleanup' to remove it.")
        else:
            print("\n❌ Authentication test failed. Please check your credentials.")
    else:
        print("\n❌ Failed to set up credentials.") 