#!/usr/bin/env python3
"""
AI analysis wrapper that tracks token usage and costs for logging.
"""

import sys
import os
from typing import Dict, Any, Optional
import json

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.analysis.gpt_utils import AIAnalyzer, ask_ai
from src.utils.run_logger import run_logger
from config import AI_PROVIDER, CLAUDE_MODEL, GPT_MODEL

class TrackedAIAnalyzer:
    """AI Analyzer wrapper that tracks usage for logging."""
    
    def __init__(self, run_id: str):
        """Initialize the tracked AI analyzer."""
        self.run_id = run_id
        self.analyzer = AIAnalyzer()
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.call_count = 0
        
        # Update run metadata with AI provider info
        run_logger.update_run(
            run_id,
            ai_provider=AI_PROVIDER,
            ai_model=CLAUDE_MODEL if AI_PROVIDER == "claude" else GPT_MODEL
        )
    
    def _call_ai_with_tracking(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.3) -> str:
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
        prompt = f"""
        Generate an executive summary for the following banking data:
        
        Counties: {data.get('counties', [])}
        Years: {data.get('years', [])}
        Total branches: {data.get('total_branches', 0)}
        Top banks: {data.get('top_banks', [])}
        
        Please provide a concise executive summary highlighting key trends and insights.
        """
        
        return self._call_ai_with_tracking(prompt, max_tokens=800)
    
    def generate_key_findings(self, data: Dict[str, Any]) -> str:
        """Generate key findings with tracking."""
        prompt = f"""
        Based on the following banking data, identify the key findings:
        
        Data: {json.dumps(data, indent=2)}
        
        Please provide 3-5 key findings about market trends, bank strategies, and community impact.
        """
        
        return self._call_ai_with_tracking(prompt, max_tokens=600)
    
    def generate_trends_analysis(self, data: Dict[str, Any]) -> str:
        """Generate trends analysis with tracking."""
        prompt = f"""
        Analyze the trends in this banking data:
        
        Data: {json.dumps(data, indent=2)}
        
        Please provide insights about year-over-year changes, market consolidation, and strategic implications.
        """
        
        return self._call_ai_with_tracking(prompt, max_tokens=700)
    
    def generate_bank_strategies_analysis(self, data: Dict[str, Any]) -> str:
        """Generate bank strategies analysis with tracking."""
        prompt = f"""
        Analyze the banking strategies evident in this data:
        
        Data: {json.dumps(data, indent=2)}
        
        Please provide insights about individual bank strategies, market positioning, and competitive dynamics.
        """
        
        return self._call_ai_with_tracking(prompt, max_tokens=700)
    
    def generate_community_impact_analysis(self, data: Dict[str, Any]) -> str:
        """Generate community impact analysis with tracking."""
        prompt = f"""
        Analyze the community impact of banking decisions in this data:
        
        Data: {json.dumps(data, indent=2)}
        
        Please provide insights about financial inclusion, community reinvestment, and access to banking services.
        """
        
        return self._call_ai_with_tracking(prompt, max_tokens=700)
    
    def generate_conclusion(self, data: Dict[str, Any]) -> str:
        """Generate conclusion with tracking."""
        prompt = f"""
        Provide a comprehensive conclusion for this banking analysis:
        
        Data: {json.dumps(data, indent=2)}
        
        Please synthesize the key insights and provide strategic recommendations.
        """
        
        return self._call_ai_with_tracking(prompt, max_tokens=500)


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