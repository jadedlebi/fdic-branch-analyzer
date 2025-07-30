#!/usr/bin/env python3
"""
Progress tracking utility for real-time progress updates during analysis.
"""

import sys
import os
from typing import Dict, Any, Optional
import json
import time

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

class ProgressTracker:
    """Tracks and reports progress during analysis."""
    
    def __init__(self, job_id: str, progress_callback=None):
        """Initialize the progress tracker."""
        self.job_id = job_id
        self.progress_callback = progress_callback
        self.current_step = "Initializing..."
        self.current_percent = 0
        self.total_steps = 0
        self.completed_steps = 0
        
        # Define the analysis steps with their progress percentages
        self.steps = {
            'initializing': {'name': 'Initializing analysis...', 'percent': 0},
            'parsing_params': {'name': 'Parsing parameters...', 'percent': 5},
            'clarifying_counties': {'name': 'Clarifying county selections...', 'percent': 10},
            'connecting_bq': {'name': 'Connecting to BigQuery...', 'percent': 15},
            'querying_data': {'name': 'Querying branch data...', 'percent': 25},
            'processing_data': {'name': 'Processing county information...', 'percent': 40},
            'building_report': {'name': 'Building Excel report...', 'percent': 55},
            'preparing_pdf': {'name': 'Preparing data for PDF...', 'percent': 65},
            'generating_ai': {'name': 'Generating AI insights...', 'percent': 75},
            'creating_pdf': {'name': 'Creating PDF report...', 'percent': 85},
            'finalizing': {'name': 'Finalizing analysis...', 'percent': 95},
            'completed': {'name': 'Analysis completed!', 'percent': 100}
        }
    
    def update_progress(self, step: str, percent: Optional[int] = None, message: Optional[str] = None):
        """Update progress for a specific step."""
        if step in self.steps:
            step_info = self.steps[step]
            self.current_step = message or step_info['name']
            self.current_percent = percent if percent is not None else step_info['percent']
            
            # Call the callback if provided
            if self.progress_callback:
                self.progress_callback(self.job_id, {
                    'step': self.current_step,
                    'percent': self.current_percent,
                    'done': False,
                    'error': None
                })
    
    def update_query_progress(self, current_query: int, total_queries: int):
        """Update progress during BigQuery queries."""
        # Query progress is between 25% and 40%
        query_percent = 25 + (current_query / total_queries) * 15
        self.update_progress('querying_data', int(query_percent), 
                           f"Querying branch data... ({current_query}/{total_queries})")
    
    def update_ai_progress(self, current_call: int, total_calls: int):
        """Update progress during AI analysis."""
        # AI progress is between 75% and 85%
        ai_percent = 75 + (current_call / total_calls) * 10
        self.update_progress('generating_ai', int(ai_percent),
                           f"Generating AI insights... ({current_call}/{total_calls})")
    
    def complete(self, success: bool = True, error: Optional[str] = None):
        """Mark the analysis as completed."""
        if success:
            if self.progress_callback:
                self.progress_callback(self.job_id, {
                    'step': 'Analysis completed!',
                    'percent': 100,
                    'done': True,
                    'error': None
                })
        else:
            if self.progress_callback:
                self.progress_callback(self.job_id, {
                    'step': self.current_step,
                    'percent': self.current_percent,
                    'done': True,
                    'error': error
                })


# Global progress storage for web interface
progress_store = {}

def get_progress(job_id: str) -> Dict[str, Any]:
    """Get current progress for a job."""
    return progress_store.get(job_id, {
        'step': 'Initializing...',
        'percent': 0,
        'done': False,
        'error': None
    })

def update_progress(job_id: str, progress_data: Dict[str, Any]):
    """Update progress for a job."""
    progress_store[job_id] = progress_data

def create_progress_tracker(job_id: str) -> ProgressTracker:
    """Create a progress tracker for a job."""
    def progress_callback(job_id: str, data: Dict[str, Any]):
        update_progress(job_id, data)
    
    return ProgressTracker(job_id, progress_callback) 