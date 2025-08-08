#!/usr/bin/env python3
"""
AI analysis utilities for FDIC bank branch data using GPT-4 and Claude.
"""

import sys
import os
import json
import numpy as np
from typing import List, Tuple, Dict, Any
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'config'))
from config import AI_PROVIDER, CLAUDE_MODEL, GPT_MODEL

# Always load the Claude API key from the environment
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

# Import the appropriate client based on provider
if AI_PROVIDER == "openai":
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
elif AI_PROVIDER == "claude":
    import anthropic
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY) if CLAUDE_API_KEY else None
else:
    client = None

def convert_numpy_types(obj):
    """Convert numpy types to native Python types for JSON serialization."""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj

def ask_ai(prompt: str) -> str:
    """Send a prompt to the configured AI provider and return the response."""
    if not client:
        raise Exception(f"No AI client configured for provider: {AI_PROVIDER}")
    
    try:
        if AI_PROVIDER == "openai":
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        elif AI_PROVIDER == "claude":
            response = client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        else:
            raise Exception(f"Unsupported AI provider: {AI_PROVIDER}")
    except Exception as e:
        raise Exception(f"Error calling {AI_PROVIDER.upper()} API: {e}")

def ask_gpt(prompt: str) -> str:
    """Legacy function name for backward compatibility."""
    return ask_ai(prompt)

def extract_parameters(prompt: str) -> Tuple[List[str], List[int]]:
    """
    Extract counties and years from a natural language prompt using AI.
    
    Args:
        prompt: Natural language prompt describing the report request
        
    Returns:
        Tuple of (counties, years) where counties is a list of strings and years is a list of integers
    """
    extraction_prompt = f"""
You are a data extraction assistant following NCRC guidelines. Extract counties and years from this request:

{prompt}

Respond with ONLY this JSON format:
{{
    "counties": ["County, Full State Name"],
    "years": [2020, 2021, 2022]
}}

Rules:
- Use "County, Full State Name" format (e.g., "Los Angeles, California")
- Major cities don't need state names unless for disambiguation
- Default counties: "Los Angeles, California", "New York, New York", "Cook, Illinois"
- Default years: [2020, 2021, 2022]
"""

    try:
        response = ask_ai(extraction_prompt)
        
        # Clean the response to extract JSON
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if not json_match:
            raise Exception("No JSON found in AI response")
        
        json_str = json_match.group()
        data = json.loads(json_str)
        
        counties = data.get('counties', [])
        years = data.get('years', [])
        
        if not counties:
            raise Exception("No counties extracted from prompt")
        if not years:
            raise Exception("No years extracted from prompt")
        
        return counties, years
        
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse JSON from AI response: {e}")
    except Exception as e:
        raise Exception(f"Error extracting parameters: {e}")

def validate_parameters(counties: List[str], years: List[int]) -> bool:
    """Validate extracted parameters."""
    if not counties or not years:
        return False
    
    # Validate years are reasonable
    current_year = 2024
    for year in years:
        if not (2000 <= year <= current_year):
            return False
    
    return True

class AIAnalyzer:
    def __init__(self):
        if AI_PROVIDER == "openai":
            from openai import OpenAI
            self.client = OpenAI(api_key=OPENAI_API_KEY)
        elif AI_PROVIDER == "claude":
            import anthropic
            self.client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
        else:
            raise Exception(f"Unsupported AI provider: {AI_PROVIDER}")
        
        self.provider = AI_PROVIDER
        self.model = OPENAI_MODEL if AI_PROVIDER == "openai" else CLAUDE_MODEL
        
    def _call_ai(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.3) -> str:
        """Make a call to the configured AI provider."""
        try:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                return response.choices[0].message.content.strip()
            elif self.provider == "claude":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text.strip()
        except Exception as e:
            print(f"Error calling {self.provider} API: {e}")
            return ""
        
    def generate_executive_summary(self, analysis_data: Dict[str, Any]) -> str:
        """Generate an executive summary of the bank branch analysis."""
        county = analysis_data['county']
        years = analysis_data['years']
        trends = analysis_data['trends']
        market_shares = analysis_data['market_shares']
        
        if not trends or not market_shares:
            return ""
            
        # Convert numpy types for JSON serialization
        trends_json = convert_numpy_types(trends)
        market_shares_json = convert_numpy_types(market_shares[:5])  # Top 5 banks only
            
        prompt = f"""
        Generate a concise executive summary for bank branch analysis of {county} from {years[0]} to {years[-1]}:

        Data: {json.dumps(trends_json, indent=2)} | {json.dumps(market_shares_json, indent=2)}

        IMPORTANT DEFINITIONS:
        - LMICT = Low-to-Moderate Income Census Tracts (areas with median family income below 80% of area median)
        - MMCT = Majority-Minority Census Tracts (areas where minority populations represent more than 50% of total population)
        - LMI/MMCT = Branches serving both low-to-moderate income and majority-minority communities

        Focus on:
        - Key trends in branch counts
        - Market concentration among major banks
        - MMCT percentage changes around 2022 (2020 census effect)
        - 2-3 paragraphs maximum

        Describe observable patterns without suggesting underlying causes.
        """
        
        return self._call_ai(prompt, max_tokens=800, temperature=0.3)
        
    def generate_key_findings(self, analysis_data: Dict[str, Any]) -> str:
        """Generate key findings from the analysis."""
        county = analysis_data['county']
        years = analysis_data['years']
        trends = analysis_data['trends']
        market_shares = analysis_data['market_shares']
        
        if not trends or not market_shares:
            return ""
            
        # Convert numpy types for JSON serialization
        trends_json = convert_numpy_types(trends)
        market_shares_json = convert_numpy_types(market_shares[:5])  # Top 5 banks only
            
        prompt = f"""
        Generate 3-5 key findings for {county} analysis from {years[0]} to {years[-1]}:

        Data: {json.dumps(trends_json, indent=2)} | {json.dumps(market_shares_json, indent=2)}

        IMPORTANT DEFINITIONS:
        - LMICT = Low-to-Moderate Income Census Tracts (areas with median family income below 80% of area median)
        - MMCT = Majority-Minority Census Tracts (areas where minority populations represent more than 50% of total population)
        - LMI/MMCT = Branches serving both low-to-moderate income and majority-minority communities

        Focus on:
        - Most significant trends and patterns
        - MMCT changes around 2022 (2020 census effect)
        - Actionable data observations
        - Format as bullet points starting with "•"

        Present factual patterns without speculating about strategic implications.
        """
        
        return self._call_ai(prompt, max_tokens=600, temperature=0.3)
        
    def analyze_overall_trends(self, analysis_data: Dict[str, Any]) -> str:
        """Analyze overall branch trends with enhanced context."""
        county = analysis_data['county']
        years = analysis_data['years']
        trends = analysis_data['trends']
        
        if not trends:
            return ""
            
        # Convert numpy types for JSON serialization
        trends_json = convert_numpy_types(trends)
            
        prompt = f"""
        Analyze overall branch trends for {county} from {years[0]} to {years[-1]}:

        Data: {json.dumps(trends_json, indent=2)}

        IMPORTANT DEFINITIONS:
        - LMICT = Low-to-Moderate Income Census Tracts (areas with median family income below 80% of area median)
        - MMCT = Majority-Minority Census Tracts (areas where minority populations represent more than 50% of total population)
        - LMI/MMCT = Branches serving both low-to-moderate income and majority-minority communities

        Focus on:
        - Overall branch count trends and year-over-year changes
        - MMCT percentage changes around 2022 (2020 census effect)
        - Three categories: LMICT, MMCT, and LMI/MMCT
        - Comparison to broader patterns where relevant
        - 2-3 paragraphs maximum

        Describe what the data demonstrates without attributing intent.
        """
        
        return self._call_ai(prompt, max_tokens=800, temperature=0.3)

    def analyze_bank_strategies(self, analysis_data: Dict[str, Any]) -> str:
        """Analyze bank strategies and market concentration."""
        county = analysis_data['county']
        years = analysis_data['years']
        market_shares = analysis_data['market_shares']
        bank_analysis = analysis_data.get('bank_analysis', [])
        
        if not market_shares:
            return ""
            
        # Convert numpy types for JSON serialization
        market_shares_json = convert_numpy_types(market_shares[:10])  # Top 10 banks
        bank_analysis_json = convert_numpy_types(bank_analysis)
            
        prompt = f"""
        Analyze market concentration in {county} from {years[0]} to {years[-1]}:

        Data: {json.dumps(market_shares_json, indent=2)} | {json.dumps(bank_analysis_json, indent=2)}

        IMPORTANT DEFINITIONS:
        - LMICT = Low-to-Moderate Income Census Tracts (areas with median family income below 80% of area median)
        - MMCT = Majority-Minority Census Tracts (areas where minority populations represent more than 50% of total population)
        - LMI/MMCT = Branches serving both low-to-moderate income and majority-minority communities

        Focus on:
        - Market concentration patterns among major banks
        - Performance differences in serving LMICT, MMCT, and LMI/MMCT communities
        - MMCT changes around 2022 (2020 census effect)
        - Competitive dynamics observable in data
        - 2-3 paragraphs maximum

        Report measurable patterns without speculating about bank strategies.
        """
        
        return self._call_ai(prompt, max_tokens=800, temperature=0.3)

    def analyze_community_impact(self, analysis_data: Dict[str, Any]) -> str:
        """Analyze community impact and branch distribution."""
        county = analysis_data['county']
        years = analysis_data['years']
        market_shares = analysis_data['market_shares']
        comparisons = analysis_data.get('comparisons', {})
        
        if not market_shares:
            return ""
            
        # Convert numpy types for JSON serialization
        market_shares_json = convert_numpy_types(market_shares[:10])  # Top 10 banks
        comparisons_json = convert_numpy_types(comparisons)
            
        prompt = f"""
        Analyze community banking patterns in {county} from {years[0]} to {years[-1]}:

        Data: {json.dumps(market_shares_json, indent=2)} | {json.dumps(comparisons_json, indent=2)}

        IMPORTANT DEFINITIONS:
        - LMICT = Low-to-Moderate Income Census Tracts (areas with median family income below 80% of area median)
        - MMCT = Majority-Minority Census Tracts (areas where minority populations represent more than 50% of total population)
        - LMI/MMCT = Branches serving both low-to-moderate income and majority-minority communities

        Focus on:
        - How banks serve different community types (LMICT, MMCT, LMI/MMCT)
        - Bank performance compared to county averages
        - 2020 census impact on MMCT designations (effective 2022)
        - Observable access patterns in data
        - 2-3 paragraphs maximum

        Describe banking access patterns without inferring underlying causes.
        """
        
        return self._call_ai(prompt, max_tokens=800, temperature=0.3)

    def generate_conclusion(self, analysis_data: Dict[str, Any]) -> str:
        """Generate a conclusion with strategic implications."""
        county = analysis_data['county']
        years = analysis_data['years']
        trends = analysis_data['trends']
        market_shares = analysis_data['market_shares']
        
        if not trends or not market_shares:
            return ""
            
        # Convert numpy types for JSON serialization
        trends_json = convert_numpy_types(trends)
        market_shares_json = convert_numpy_types(market_shares[:5])  # Top 5 banks
            
        prompt = f"""
        Generate conclusion for {county} analysis from {years[0]} to {years[-1]}:

        Data: {json.dumps(trends_json, indent=2)} | {json.dumps(market_shares_json, indent=2)}

        IMPORTANT DEFINITIONS:
        - LMICT = Low-to-Moderate Income Census Tracts (areas with median family income below 80% of area median)
        - MMCT = Majority-Minority Census Tracts (areas where minority populations represent more than 50% of total population)
        - LMI/MMCT = Branches serving both low-to-moderate income and majority-minority communities

        Focus on:
        - Key data patterns using proper formatting
        - Three community categories (LMICT, MMCT, LMI/MMCT)
        - 2020 census impact on MMCT data
        - Observable trends and their measurable effects
        - 2-3 paragraphs maximum

        Synthesize key data insights without making policy suggestions.
        """
        
        return self._call_ai(prompt, max_tokens=800, temperature=0.3)


# Legacy class name for backward compatibility
class GPTAnalyzer(AIAnalyzer):
    """Legacy class name - now uses the configured AI provider."""
    pass