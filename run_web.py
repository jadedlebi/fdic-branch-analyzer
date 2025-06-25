#!/usr/bin/env python3
"""
Web interface launcher for FDIC Branch Analyzer
"""

import os
import sys
from app import app

if __name__ == '__main__':
    print("🚀 Starting FDIC Branch Analyzer Web Interface...")
    print("📱 Open your browser and go to: http://127.0.0.1:5050")
    print("⏹️  Press Ctrl+C to stop the server")
    print()
    
    # Set environment variables if not already set
    if not os.getenv('SECRET_KEY'):
        os.environ['SECRET_KEY'] = 'fdic-branch-analyzer-secret-key-2024'
    
    # Run the Flask app on a different port and only on localhost
    app.run(debug=True, host='127.0.0.1', port=5050) 