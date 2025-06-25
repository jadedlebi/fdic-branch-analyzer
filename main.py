#!/usr/bin/env python3
"""
AI-assisted FDIC Bank Branch Report Generator
Entry point for the application.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the main application
from core.main import main

if __name__ == "__main__":
    main()
