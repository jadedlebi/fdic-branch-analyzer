#!/usr/bin/env python3
"""
AI analysis wrapper that tracks token usage and costs for logging.
"""

import sys
import os
from typing import Dict, Any, Optional
import json
import pandas as pd
import numpy as np

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.analysis.gpt_utils import AIAnalyzer, ask_ai, convert_numpy_types
from src.utils.run_logger import run_logger
from config import AI_PROVIDER, CLAUDE_MODEL, GPT_MODEL

def convert_dataframe_to_json_serializable(data: Any) -> Any:
    """Convert DataFrame and numpy types to JSON-serializable format."""
    if isinstance(data, pd.DataFrame):
        # Convert DataFrame to records and handle numpy types
        records = data.to_dict('records')
        return convert_numpy_types(records)
    elif isinstance(data, dict):
        # Recursively convert dictionary values
        return {key: convert_dataframe_to_json_serializable(value) for key, value in data.items()}
    elif isinstance(data, list):
        # Recursively convert list items
        return [convert_dataframe_to_json_serializable(item) for item in data]
    else:
        # Use the existing numpy type conversion
        return convert_numpy_types(data)

class TrackedAIAnalyzer:
    """AI Analyzer wrapper that tracks usage for logging."""
    
    def __init__(self, run_id: str, progress_tracker=None):
        """Initialize the tracked AI analyzer."""
        self.run_id = run_id
        self.analyzer = AIAnalyzer()
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.call_count = 0
        self.progress_tracker = progress_tracker
        
        # Update run metadata with AI provider info
        run_logger.update_run(
            run_id,
            ai_provider=AI_PROVIDER,
            ai_model=CLAUDE_MODEL if AI_PROVIDER == "claude" else GPT_MODEL
        )
    
    def _call_ai_with_tracking(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.3, call_index: int = None, total_calls: int = None) -> str:
        """Make an AI call and track token usage."""
        try:
            # Make the actual AI call
            response = self.analyzer._call_ai(prompt, max_tokens, temperature)
            
            # Estimate token usage (rough approximation)
            input_tokens = len(prompt.split()) * 1.3  # Rough estimate
            output_tokens = len(response.split()) * 1.3  # Rough estimate
            
            # Update tracking
            self.total_input_tokens += int(input_tokens)
            self.total_output_tokens += int(output_tokens)
            self.call_count += 1
            
            # Update progress if tracker is available
            if self.progress_tracker and call_index is not None and total_calls is not None:
                self.progress_tracker.update_ai_progress(call_index + 1, total_calls)
            
            # Update run metadata
            run_logger.update_run(
                self.run_id,
                ai_calls=self.call_count,
                ai_input_tokens=self.total_input_tokens,
                ai_output_tokens=self.total_output_tokens
            )
            
            return response
            
        except Exception as e:
            print(f"Error in tracked AI call: {e}")
            return ""
    
    def generate_executive_summary(self, data: Dict[str, Any]) -> str:
        """Generate executive summary with tracking."""
        # Convert data to JSON-serializable format
        json_data = convert_dataframe_to_json_serializable(data)
        
        prompt = f"""
        Generate an executive summary for the following banking data:
        
        Counties: {json_data.get('counties', [])}
        Years: {json_data.get('years', [])}
        Total branches: {json_data.get('total_branches', 0)}
        Top banks: {json_data.get('top_banks', [])}
        
        Please provide a concise executive summary highlighting key trends and insights.
        """
        
        return self._call_ai_with_tracking(prompt, max_tokens=800, call_index=0, total_calls=6)
    
    def generate_key_findings(self, data: Dict[str, Any]) -> str:
        """Generate key findings with tracking."""
        # Convert data to JSON-serializable format
        json_data = convert_dataframe_to_json_serializable(data)
        
        prompt = f"""
        Based on the following banking data, identify the key findings:
        
        Counties: {json_data.get('counties', [])}
        Years: {json_data.get('years', [])}
        Total branches: {json_data.get('total_branches', 0)}
        Top banks: {json_data.get('top_banks', [])}
        Data: {json.dumps(json_data.get('data', []), indent=2)}
        
        Please provide 3-5 key findings about market trends, bank strategies, and community impact.
        """
        
        return self._call_ai_with_tracking(prompt, max_tokens=600, call_index=1, total_calls=6)
    
    def generate_trends_analysis(self, data: Dict[str, Any]) -> str:
        """Generate trends analysis with tracking."""
        # Convert data to JSON-serializable format
        json_data = convert_dataframe_to_json_serializable(data)
        
        prompt = f"""
        Analyze the trends in this banking data:
        
        Counties: {json_data.get('counties', [])}
        Years: {json_data.get('years', [])}
        Data: {json.dumps(json_data.get('data', []), indent=2)}
        
        Please provide insights about year-over-year changes, market consolidation, and strategic implications.
        """
        
        return self._call_ai_with_tracking(prompt, max_tokens=700, call_index=2, total_calls=6)
    
    def generate_bank_strategies_analysis(self, data: Dict[str, Any]) -> str:
        """Generate bank strategies analysis with tracking."""
        # Convert data to JSON-serializable format
        json_data = convert_dataframe_to_json_serializable(data)
        
        prompt = f"""
        Analyze the banking strategies evident in this data:
        
        Counties: {json_data.get('counties', [])}
        Years: {json_data.get('years', [])}
        Top banks: {json_data.get('top_banks', [])}
        Data: {json.dumps(json_data.get('data', []), indent=2)}
        
        Please provide insights about individual bank strategies, market positioning, and competitive dynamics.
        """
        
        return self._call_ai_with_tracking(prompt, max_tokens=700, call_index=3, total_calls=6)
    
    def generate_community_impact_analysis(self, data: Dict[str, Any]) -> str:
        """Generate community impact analysis with tracking."""
        # Convert data to JSON-serializable format
        json_data = convert_dataframe_to_json_serializable(data)
        
        prompt = f"""
        Analyze the community impact of banking decisions in this data:
        
        Counties: {json_data.get('counties', [])}
        Years: {json_data.get('years', [])}
        Data: {json.dumps(json_data.get('data', []), indent=2)}
        
        Please provide insights about financial inclusion, community reinvestment, and access to banking services.
        """
        
        return self._call_ai_with_tracking(prompt, max_tokens=700, call_index=4, total_calls=6)
    
    def generate_conclusion(self, data: Dict[str, Any]) -> str:
        """Generate conclusion with tracking."""
        # Convert data to JSON-serializable format
        json_data = convert_dataframe_to_json_serializable(data)
        
        prompt = f"""
        Provide a comprehensive conclusion for this banking analysis:
        
        Counties: {json_data.get('counties', [])}
        Years: {json_data.get('years', [])}
        Total branches: {json_data.get('total_branches', 0)}
        Top banks: {json_data.get('top_banks', [])}
        Data: {json.dumps(json_data.get('data', []), indent=2)}
        
        Please synthesize the key insights and provide strategic recommendations.
        """
        
        return self._call_ai_with_tracking(prompt, max_tokens=500, call_index=5, total_calls=6)


def track_ai_call(run_id: str, prompt: str, max_tokens: int = 1000) -> str:
    """Track a single AI call for logging purposes."""
    try:
        # Make the AI call
        response = ask_ai(prompt)
        
        # Estimate token usage
        input_tokens = len(prompt.split()) * 1.3
        output_tokens = len(response.split()) * 1.3
        
        # Update run metadata
        run_logger.update_run(
            run_id,
            ai_calls=1,
            ai_input_tokens=int(input_tokens),
            ai_output_tokens=int(output_tokens),
            ai_provider=AI_PROVIDER,
            ai_model=CLAUDE_MODEL if AI_PROVIDER == "claude" else GPT_MODEL
        )
        
        return response
        
    except Exception as e:
        print(f"Error in tracked AI call: {e}")
        return "" 