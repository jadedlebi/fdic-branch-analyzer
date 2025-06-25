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
You are a data extraction assistant. Given the following report request, extract the counties and years mentioned.

Report request: {prompt}

Please respond with ONLY a JSON object in this exact format:
{{
    "counties": ["county1, state", "county2, state"],
    "years": [2020, 2021, 2022]
}}

Rules:
- Counties should be in "County, State" format (e.g., "Los Angeles, CA")
- Years should be integers
- If no specific counties are mentioned, use common counties like "Los Angeles, CA", "New York, NY", "Cook, IL"
- If no specific years are mentioned, use recent years like [2020, 2021, 2022]
- Return ONLY the JSON, no other text
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
        Generate a concise executive summary for the bank branch analysis of {county} from {years[0]} to {years[-1]} based on the following data:

        Trends Data:
        {json.dumps(trends_json, indent=2)}

        Market Share Data:
        {json.dumps(market_shares_json, indent=2)}

        Provide an executive summary that:
        1. Summarizes the key trends in branch counts over the period
        2. Highlights the market concentration among major banks
        3. Identifies the most significant changes and their implications
        4. Mentions key strategic insights for stakeholders
        5. Is written in a professional, executive-level tone
        6. Is concise but comprehensive (2-3 paragraphs maximum)

        Write in a professional, executive summary style that would be suitable for senior management or board members.
        """
        
        return self._call_ai(prompt, max_tokens=600, temperature=0.3)
        
    def generate_key_findings(self, analysis_data: Dict[str, Any]) -> str:
        """Generate key findings from the bank branch analysis."""
        county = analysis_data['county']
        years = analysis_data['years']
        trends = analysis_data['trends']
        market_shares = analysis_data['market_shares']
        bank_analysis = analysis_data['bank_analysis']
        
        if not trends or not market_shares:
            return ""
            
        # Convert numpy types for JSON serialization
        trends_json = convert_numpy_types(trends)
        market_shares_json = convert_numpy_types(market_shares[:5])  # Top 5 banks only
        bank_analysis_json = convert_numpy_types(bank_analysis)
            
        prompt = f"""
        Generate key findings for the bank branch analysis of {county} from {years[0]} to {years[-1]} based on the following data:

        Trends Data:
        {json.dumps(trends_json, indent=2)}

        Market Share Data:
        {json.dumps(market_shares_json, indent=2)}

        Bank Growth Analysis:
        {json.dumps(bank_analysis_json, indent=2)}

        Provide 5-7 key findings that:
        1. Highlight the most important trends and patterns
        2. Identify significant market concentration issues
        3. Point out notable bank performance differences
        4. Emphasize community impact implications
        5. Suggest strategic implications for the banking sector
        6. Are written as bullet points or numbered findings
        7. Use specific data points and percentages where relevant

        Format as a list of key findings, each 1-2 sentences long, focusing on the most impactful insights.
        """
        
        return self._call_ai(prompt, max_tokens=800, temperature=0.3)
        
    def analyze_overall_trends(self, analysis_data: Dict[str, Any]) -> str:
        """Generate AI analysis of overall branch trends."""
        county = analysis_data['county']
        years = analysis_data['years']
        trends = analysis_data['trends']
        
        if not trends:
            return ""
            
        # Convert numpy types for JSON serialization
        trends_json = convert_numpy_types(trends)
            
        prompt = f"""
        Analyze the overall bank branch trends for {county} from {years[0]} to {years[-1]} based on the following data:

        {json.dumps(trends_json, indent=2)}

        Provide a comprehensive analysis that includes:
        1. Total branch count changes and percentage changes over the period
        2. Year-over-year patterns (steady decline, fluctuations, recovery, etc.)
        3. Analysis of LMI (Low-to-Moderate Income) tract distribution trends
        4. Analysis of Majority-Minority tract distribution trends
        5. Analysis of tracts that are both LMI and Majority-Minority
        6. Industry context and potential explanations for trends
        7. Comparison of different metrics and their correlations
        8. Implications for financial inclusion and community access

        Write in a professional, analytical tone similar to a research report. Focus on insights and explanations, not just data recitation. 
        Format as 2-3 cohesive paragraphs that flow naturally and provide deep analytical insights.
        """
        
        return self._call_ai(prompt, max_tokens=1200, temperature=0.3)

    def analyze_bank_strategies(self, analysis_data: Dict[str, Any]) -> str:
        """Generate AI analysis of bank strategies and market concentration."""
        county = analysis_data['county']
        years = analysis_data['years']
        market_shares = analysis_data['market_shares']
        bank_analysis = analysis_data['bank_analysis']
        
        if not market_shares or not bank_analysis:
            return ""
            
        # Convert numpy types for JSON serialization
        market_shares_json = convert_numpy_types(market_shares)
        bank_analysis_json = convert_numpy_types(bank_analysis)
            
        prompt = f"""
        Analyze the bank strategies and market concentration for {county} from {years[0]} to {years[-1]} based on the following data:

        Market Share Data:
        {json.dumps(market_shares_json, indent=2)}

        Bank Growth Analysis:
        {json.dumps(bank_analysis_json, indent=2)}

        Provide a comprehensive analysis that includes:
        1. Market concentration analysis (how many banks control what percentage of branches)
        2. Individual bank performance and strategy insights
        3. Growth/decline patterns and potential explanations
        4. Comparison of different banks' approaches and market positioning
        5. Industry consolidation trends and their impact on competition
        6. Strategic implications for the banking landscape
        7. Analysis of market power and potential antitrust considerations
        8. Implications for consumer choice and service quality

        Write in a professional, analytical tone. Focus on strategic insights and explanations for why banks made certain decisions.
        Format as 2-3 cohesive paragraphs that provide deep strategic analysis.
        """
        
        return self._call_ai(prompt, max_tokens=1200, temperature=0.3)

    def analyze_community_impact(self, analysis_data: Dict[str, Any]) -> str:
        """Generate AI analysis of community impact and branch distribution."""
        county = analysis_data['county']
        years = analysis_data['years']
        market_shares = analysis_data['market_shares']
        comparisons = analysis_data['comparisons']
        
        if not market_shares or not comparisons:
            return ""
            
        # Convert numpy types for JSON serialization
        market_shares_json = convert_numpy_types(market_shares)
        comparisons_json = convert_numpy_types(comparisons)
            
        prompt = f"""
        Analyze the community impact and branch distribution patterns for {county} from {years[0]} to {years[-1]} based on the following data:

        Market Share Data (including LMI and MMCT percentages):
        {json.dumps(market_shares_json, indent=2)}

        County Average Comparisons:
        {json.dumps(comparisons_json, indent=2)}

        Provide a comprehensive analysis that includes:
        1. How different banks serve LMI (Low-to-Moderate Income) communities
        2. How different banks serve Majority-Minority communities
        3. Which banks are more focused on underserved areas vs. affluent areas
        4. Community access implications of branch distribution patterns
        5. Fair lending and community reinvestment implications
        6. Recommendations for improving financial inclusion
        7. Analysis of geographic equity in branch distribution
        8. Impact on economic development and community stability
        9. Comparison of bank performance against community needs
        10. Strategic recommendations for policymakers and regulators

        Write in a professional, analytical tone. Focus on community impact and access to financial services.
        Format as 2-3 cohesive paragraphs that provide comprehensive community impact analysis.
        """
        
        return self._call_ai(prompt, max_tokens=1200, temperature=0.3)

    def generate_conclusion(self, analysis_data: Dict[str, Any]) -> str:
        """Generate AI-powered conclusion synthesizing all findings."""
        county = analysis_data['county']
        years = analysis_data['years']
        trends = analysis_data['trends']
        market_shares = analysis_data['market_shares']
        bank_analysis = analysis_data['bank_analysis']
        comparisons = analysis_data['comparisons']
        
        # Convert numpy types for JSON serialization
        trends_json = convert_numpy_types(trends)
        market_shares_json = convert_numpy_types(market_shares)
        bank_analysis_json = convert_numpy_types(bank_analysis)
        comparisons_json = convert_numpy_types(comparisons)
        
        prompt = f"""
        Generate a comprehensive conclusion for the bank branch analysis of {county} from {years[0]} to {years[-1]} based on all the data:

        Trends Data:
        {json.dumps(trends_json, indent=2)}

        Market Share Data:
        {json.dumps(market_shares_json, indent=2)}

        Bank Analysis:
        {json.dumps(bank_analysis_json, indent=2)}

        Comparisons:
        {json.dumps(comparisons_json, indent=2)}

        Provide a conclusion that:
        1. Summarizes the key findings about branch trends and market concentration
        2. Explains the implications for the banking industry and competition
        3. Discusses the impact on community access to financial services
        4. Identifies patterns in bank strategies and their effectiveness
        5. Suggests what these trends mean for the future of banking
        6. Provides insights about financial inclusion and community development
        7. Offers strategic recommendations for stakeholders
        8. Addresses potential policy implications
        9. Considers the balance between efficiency and accessibility
        10. Outlines next steps for monitoring and improvement

        Write in a professional, analytical tone. This should be a comprehensive conclusion that ties together all the analysis.
        Format as 2-3 cohesive paragraphs that provide strategic insights and forward-looking recommendations.
        """
        
        return self._call_ai(prompt, max_tokens=1000, temperature=0.3)


# Legacy class name for backward compatibility
class GPTAnalyzer(AIAnalyzer):
    """Legacy class name - now uses the configured AI provider."""
    pass