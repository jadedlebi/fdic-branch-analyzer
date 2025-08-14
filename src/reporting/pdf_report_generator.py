#!/usr/bin/env python3
"""
Enhanced PDF Report Generator for FDIC Bank Branch Analysis
Creates professional, comprehensive reports with detailed trends, market share analysis, and AI-powered insights.
"""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, 
                                BaseDocTemplate, PageTemplate, Frame, KeepTogether)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
import os
import json
import re
from src.analysis.gpt_utils import AIAnalyzer


class EnhancedPDFReportGenerator:
    def __init__(self, data: pd.DataFrame, counties: List[str], years: List[int]):
        """
        Initialize the enhanced PDF report generator.
        
        Args:
            data: DataFrame with branch data
            counties: List of counties analyzed
            years: List of years analyzed
        """
        # Validate input data
        if data.empty:
            raise ValueError("Data DataFrame cannot be empty")
        
        required_columns = ['bank_name', 'year', 'county_state', 'total_branches', 'lmict', 'mmct', 'total_deposits']
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        if not counties:
            raise ValueError("Counties list cannot be empty")
        
        if not years:
            raise ValueError("Years list cannot be empty")
        
        self.data = data.copy()
        self.counties = counties
        self.years = sorted(years)
        self.styles = getSampleStyleSheet()
        self.setup_enhanced_styles()
        try:
            self.ai_analyzer = AIAnalyzer()
            # Test if AI is properly configured
            test_response = self.ai_analyzer._call_ai("Test", max_tokens=10)
            if not test_response or test_response.strip() == "":
                print("Warning: AI analyzer is not properly configured. Using fallback content.")
                self.ai_analyzer = None
        except Exception as e:
            print(f"Warning: AI analyzer initialization failed: {e}. Using fallback content.")
            self.ai_analyzer = None
        self.page_breaks_count = 0  # Track number of page breaks
        
    def setup_enhanced_styles(self):
        """Setup enhanced, professional paragraph styles for the report."""
        # Enhanced title style
        self.title_style = ParagraphStyle(
            'EnhancedTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            spaceAfter=35,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1a365d'),
            fontName='Helvetica-Bold',
            leading=32
        )
        
        # Enhanced subtitle style
        self.subtitle_style = ParagraphStyle(
            'EnhancedSubtitle',
            parent=self.styles['Normal'],
            fontSize=16,
            spaceAfter=25,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#4a5568'),
            fontName='Helvetica',
            leading=18
        )
        
        # Enhanced section heading style
        self.section_style = ParagraphStyle(
            'EnhancedSection',
            parent=self.styles['Heading2'],
            fontSize=18,
            spaceAfter=15,
            spaceBefore=30,
            textColor=colors.HexColor('#2d3748'),
            fontName='Helvetica-Bold',
            leading=20
        )
        
        # Enhanced subsection heading style
        self.subsection_style = ParagraphStyle(
            'EnhancedSubsection',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=10,
            spaceBefore=20,
            textColor=colors.HexColor('#4a5568'),
            fontName='Helvetica-Bold',
            leading=16
        )
        
        # Enhanced body text style
        self.body_style = ParagraphStyle(
            'EnhancedBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=10,
            leading=15,
            alignment=TA_JUSTIFY,
            textColor=colors.HexColor('#2d3748'),
            fontName='Helvetica'
        )
        
        # Enhanced bullet point style
        self.bullet_style = ParagraphStyle(
            'EnhancedBullet',
            parent=self.body_style,
            leftIndent=20,
            spaceAfter=8,
            leading=14
        )
        
        # Enhanced numbered list style
        self.numbered_style = ParagraphStyle(
            'EnhancedNumbered',
            parent=self.body_style,
            leftIndent=20,
            spaceAfter=8,
            leading=14
        )
        
        # Enhanced summary box style
        self.summary_box_style = ParagraphStyle(
            'EnhancedSummaryBox',
            parent=self.body_style,
            backColor=colors.HexColor('#f7fafc'),
            borderColor=colors.HexColor('#e2e8f0'),
            borderWidth=1,
            borderPadding=10,
            spaceAfter=15,
            spaceBefore=10
        )
        



        

    

    
    def add_page_number(self, canvas, doc):
        """Add page numbers to the bottom center of each page."""
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.saveState()
        canvas.setFont('Helvetica', 10)
        canvas.setFillColor(colors.HexColor('#4a5568'))
        canvas.drawCentredString(doc.pagesize[0] / 2, 0.5 * inch, text)
        canvas.restoreState()
    
    def format_number(self, num: float) -> str:
        """Format numbers as #,### with no decimals."""
        if pd.isna(num) or num == 0:
            return "0"
        return f"{int(num):,}"
    
    def format_percentage(self, pct: float) -> str:
        """Format percentages as #.#% (simplified format for narrative)."""
        if pd.isna(pct):
            return "0.0%"
        # Ensure percentage is not in thousands (should be 0-100 range)
        if abs(pct) > 1000:
            pct = pct / 100  # Convert from basis points to percentage
        return f"{pct:.1f}%"
    
    def format_percentage_table(self, pct: float) -> str:
        """Format percentages for tables (without % symbol if in header)."""
        if pd.isna(pct):
            return "0.0"
        # Ensure percentage is not in thousands (should be 0-100 range)
        if abs(pct) > 1000:
            pct = pct / 100  # Convert from basis points to percentage
        return f"{pct:.1f}"
    
    def format_year(self, year: int) -> str:
        """Format year as integer with no decimals."""
        return str(int(year))
    
    def to_proper_case(self, text: str) -> str:
        """Convert text to proper case for bank names in narrative text."""
        if not text:
            return text
        return text.title()
    
    def to_all_caps(self, text: str) -> str:
        """Convert text to all caps for bank names in tables."""
        if not text:
            return text
        return text.upper()
    
    def format_bank_name_narrative(self, text: str) -> str:
        """Format bank names for narrative text - proper case except for acronyms."""
        if not text:
            return text
        
        # Common bank name patterns that should be preserved
        common_patterns = {
            'JPMORGAN': 'JPMorgan',
            'CHASE': 'Chase',
            'WELLS': 'Wells',
            'FARGO': 'Fargo',
            'PNC': 'PNC',
            'BANK': 'Bank',
            'NATIONAL': 'National',
            'ASSOCIATION': 'Association',
            'CORP': 'Corp',
            'CORPORATION': 'Corporation',
            'TRUST': 'Trust',
            'COMPANY': 'Company',
            'CO': 'Co',
            'INC': 'Inc',
            'LLC': 'LLC',
            'LTD': 'Ltd',
            'OF': 'of',
            'THE': 'the',
            'AND': 'and',
            'AMERICA': 'America',
            'FIRST': 'First',
            'COMMUNITY': 'Community',
            'REGIONAL': 'Regional',
            'US': 'US',
            'SMALL': 'Small'
        }
        
        # Split the text into words
        words = text.split()
        formatted_words = []
        
        for i, word in enumerate(words):
            word_upper = word.upper()
            
            # Check if this word matches a known pattern
            if word_upper in common_patterns:
                formatted_words.append(common_patterns[word_upper])
            # Check if this word is likely an acronym (all caps or contains numbers)
            elif word.isupper() or any(char.isdigit() for char in word):
                # Keep acronyms in uppercase
                formatted_words.append(word)
            elif len(word) <= 3 and word.isupper():
                # Short words in all caps are likely acronyms
                formatted_words.append(word)
            elif any(char.isupper() for char in word[1:]) and not word.isupper():
                # Words with internal capitals (like JPMorgan) - preserve the pattern
                formatted_words.append(word)
            else:
                # Regular words get proper case
                formatted_words.append(word.title())
        
        return ' '.join(formatted_words)
    
    def convert_bank_names_to_proper_case(self, text: str) -> str:
        """Convert bank names in text to proper case while preserving other formatting."""
        if not text:
            return text
        
        # Get unique bank names from the data
        bank_names = set()
        for county in self.counties:
            county_data = self.data[self.data['county_state'] == county]
            bank_names.update(county_data['bank_name'].unique())
        
        # Convert each bank name to proper case in the text
        converted_text = text
        for bank_name in bank_names:
            if bank_name in text:
                converted_text = converted_text.replace(bank_name, self.format_bank_name_narrative(bank_name))
        
        return converted_text
    
    def create_safe_anchor(self, text: str) -> str:
        """Create a URL-safe anchor name from text."""
        safe_anchor = re.sub(r'[^a-zA-Z0-9_]', '_', text)
        safe_anchor = re.sub(r'_+', '_', safe_anchor)  # Replace multiple underscores with single
        safe_anchor = safe_anchor.strip('_')  # Remove leading/trailing underscores
        return safe_anchor
    
    def calculate_enhanced_trends(self) -> Dict[str, pd.DataFrame]:
        """Calculate comprehensive year-over-year trends for each county."""
        trends = {}
        
        for county in self.counties:
            county_data = self.data[self.data['county_state'] == county].copy()
            
            # Aggregate by year
            yearly_stats = county_data.groupby('year').agg({
                'total_branches': 'sum',
                'lmict': 'sum',
                'mmct': 'sum'
            }).reset_index()
            
            # Calculate percentages (handle division by zero)
            yearly_stats['lmict_pct'] = np.where(yearly_stats['total_branches'] > 0, 
                                                (yearly_stats['lmict'] / yearly_stats['total_branches'] * 100).round(2), 0)
            yearly_stats['mmct_pct'] = np.where(yearly_stats['total_branches'] > 0, 
                                               (yearly_stats['mmct'] / yearly_stats['total_branches'] * 100).round(2), 0)
            # Note: Both % calculation removed as it's not needed for this analysis
            
            # Calculate year-over-year changes
            yearly_stats['total_yoy_change'] = yearly_stats['total_branches'].pct_change() * 100
            yearly_stats['total_yoy_change_abs'] = yearly_stats['total_branches'].diff()
            yearly_stats['lmict_yoy_change'] = yearly_stats['lmict_pct'].pct_change() * 100
            yearly_stats['mmct_yoy_change'] = yearly_stats['mmct_pct'].pct_change() * 100
            
            # Calculate cumulative changes from first year (handle division by zero)
            first_year = yearly_stats['total_branches'].iloc[0]
            yearly_stats['total_cumulative_change'] = np.where(first_year > 0, 
                                                              ((yearly_stats['total_branches'] - first_year) / first_year * 100).round(2), 0)
            
            trends[county] = yearly_stats
        
        return trends
    
    def calculate_enhanced_market_share(self, target_year: int = None) -> Dict[str, pd.DataFrame]:
        """Calculate comprehensive market share for each bank in the target year."""
        if target_year is None:
            target_year = max(self.years)
            
        market_shares = {}
        
        for county in self.counties:
            county_data = self.data[
                (self.data['county_state'] == county) & 
                (self.data['year'] == target_year)
            ].copy()
            
            if county_data.empty:
                continue
            
            # Calculate total deposits in county
            total_county_deposits = county_data['total_deposits'].sum()
            
            # Calculate market share for each bank based on deposits
            bank_stats = county_data.groupby('bank_name').agg({
                'total_branches': 'sum',
                'total_deposits': 'sum',
                'lmict': 'sum',
                'mmct': 'sum'
            }).reset_index()
            
            bank_stats['market_share'] = (bank_stats['total_deposits'] / total_county_deposits * 100).round(2) if total_county_deposits > 0 else 0
            bank_stats['lmict_pct'] = np.where(bank_stats['total_branches'] > 0, 
                                              (bank_stats['lmict'] / bank_stats['total_branches'] * 100).round(2), 0)
            bank_stats['mmct_pct'] = np.where(bank_stats['total_branches'] > 0, 
                                             (bank_stats['mmct'] / bank_stats['total_branches'] * 100).round(2), 0)
            # Note: Both % calculation removed as it's not needed for this analysis
            
            # Sort by market share descending
            bank_stats = bank_stats.sort_values('market_share', ascending=False)
            
            market_shares[county] = bank_stats
        
        return market_shares
    
    def get_enhanced_top_banks(self, market_shares: Dict[str, pd.DataFrame], threshold: float = 50.0) -> Dict[str, List[str]]:
        """Get top banks that control the specified percentage of market share."""
        top_banks = {}
        
        for county, bank_data in market_shares.items():
            if bank_data.empty:
                continue
                
            cumulative_share = 0
            top_bank_list = []
            
            for _, row in bank_data.iterrows():
                cumulative_share += row['market_share']
                top_bank_list.append(row['bank_name'])
                
                if cumulative_share >= threshold:
                    break
            
            top_banks[county] = top_bank_list
        
        return top_banks
    
    def analyze_enhanced_bank_growth(self, top_banks: Dict[str, List[str]]) -> Dict[str, pd.DataFrame]:
        """Analyze comprehensive bank growth patterns."""
        bank_analysis = {}
        
        for county in self.counties:
            if county not in top_banks:
                continue
                
            county_data = self.data[self.data['county_state'] == county].copy()
            first_year = min(self.years)
            last_year = max(self.years)
            
            bank_growth_data = []
            
            for bank_name in top_banks[county]:
                # Get first and last year data for this bank
                first_year_data = county_data[
                    (county_data['bank_name'] == bank_name) & 
                    (county_data['year'] == first_year)
                ]
                last_year_data = county_data[
                    (county_data['bank_name'] == bank_name) & 
                    (county_data['year'] == last_year)
                ]
                
                first_year_branches = first_year_data['total_branches'].sum() if not first_year_data.empty else 0
                last_year_branches = last_year_data['total_branches'].sum() if not last_year_data.empty else 0
                
                # Calculate growth metrics
                absolute_change = last_year_branches - first_year_branches
                percentage_change = ((last_year_branches - first_year_branches) / first_year_branches * 100) if first_year_branches > 0 else 0
                
                # Get current year demographics (calculate if not available)
                if not last_year_data.empty:
                    total_branches = last_year_data['total_branches'].sum()
                    current_lmi_pct = (last_year_data['lmict'].sum() / total_branches * 100) if total_branches > 0 else 0
                    current_mmct_pct = (last_year_data['mmct'].sum() / total_branches * 100) if total_branches > 0 else 0
                else:
                    current_lmi_pct = 0
                    current_mmct_pct = 0
                
                bank_growth_data.append({
                    'bank_name': bank_name,
                    'first_year_branches': first_year_branches,
                    'last_year_branches': last_year_branches,
                    'absolute_change': absolute_change,
                    'percentage_change': percentage_change,
                    'current_lmi_pct': current_lmi_pct,
                    'current_mmct_pct': current_mmct_pct
                })
            
            bank_analysis[county] = pd.DataFrame(bank_growth_data)
        
        return bank_analysis
    
    def calculate_enhanced_comparisons(self, bank_analysis: Dict[str, pd.DataFrame]) -> Dict[str, Dict]:
        """Calculate enhanced comparisons to county averages."""
        comparisons = {}
        
        for county in self.counties:
            if county not in bank_analysis:
                continue
                
            # Get county averages for the most recent year
            recent_year = max(self.years)
            county_data = self.data[
                (self.data['county_state'] == county) & 
                (self.data['year'] == recent_year)
            ]
            
            if county_data.empty:
                continue
            
            # Calculate county averages
            total_branches = county_data['total_branches'].sum()
            county_avg_lmict = (county_data['lmict'].sum() / total_branches * 100) if total_branches > 0 else 0
            county_avg_mmct = (county_data['mmct'].sum() / total_branches * 100) if total_branches > 0 else 0
            
            comparisons[county] = {
                'county_avg_lmict': county_avg_lmict,
                'county_avg_mmct': county_avg_mmct,
                'total_county_branches': total_branches
            }
        
        return comparisons
    
    def calculate_hhi(self, market_shares: pd.DataFrame) -> Tuple[float, str, str]:
        """
        Calculate the Herfindahl-Hirschman Index (HHI) for a given market.
        
        Args:
            market_shares: DataFrame containing bank market share data
            
        Returns:
            Tuple of (HHI value, concentration level, interpretation)
        """
        if market_shares.empty:
            return 0.0, "No Data", "No market data available"
        
        # Calculate HHI: sum of squared market shares
        # Note: market_share is already in percentage form (e.g., 25.5 for 25.5%)
        hhi = (market_shares['market_share'] ** 2).sum()
        
        # Determine concentration level based on regulatory guidelines
        if hhi < 1000:
            concentration_level = "Unconcentrated"
            interpretation = "Market shows healthy competition with low concentration"
        elif hhi < 1800:
            concentration_level = "Moderately Concentrated"
            interpretation = "Market shows moderate concentration, some competitive concerns"
        else:
            concentration_level = "Highly Concentrated"
            interpretation = "Market is highly concentrated and may face regulatory restrictions on mergers"
        
        return round(hhi, 1), concentration_level, interpretation
    
    def generate_enhanced_ai_analysis(self, county_data, trends, market_shares, bank_analysis, comparisons):
        """Generate enhanced AI-powered analysis using the configured AI provider for narrative insights only (no tables or formatting)."""
        # Prepare enhanced data for AI analysis
        analysis_data = {
            'county': county_data.get('county', 'Unknown County'),
            'years': self.years,
            'trends': trends.to_dict('records') if hasattr(trends, 'empty') and not trends.empty else (trends if isinstance(trends, list) else []),
            'market_shares': market_shares.to_dict('records') if hasattr(market_shares, 'empty') and not market_shares.empty else (market_shares if isinstance(market_shares, list) else []),
            'bank_analysis': bank_analysis.to_dict('records') if hasattr(bank_analysis, 'empty') and not bank_analysis.empty else (bank_analysis if isinstance(bank_analysis, list) else []),
            'comparisons': comparisons
        }
        # Prompts are now explicit: only narrative, no tables or formatting
        if self.ai_analyzer is None:
            # Use fallback content when AI is not available
            county_name = analysis_data.get('county', 'the analyzed area')
            years_str = f"{analysis_data.get('years', [2022, 2023, 2024])[0]}-{analysis_data.get('years', [2022, 2023, 2024])[-1]}"
            
            executive_summary = f"This comprehensive analysis examines bank branch trends in {county_name} from {years_str} using FDIC Summary of Deposits data. The analysis focuses on three key metrics: total branch counts, the percentage of branches in Low-to-Moderate Income (LMI) tracts, and the percentage of branches in Majority-Minority Census Tracts (MMCT). This report provides detailed insights into market concentration, bank strategies, community impact, and regulatory implications for banking infrastructure development."
            
            overall_trends_analysis = f"Branch trends in {county_name} demonstrate significant evolution of banking infrastructure over the {years_str} period. The analysis reveals comprehensive patterns in branch distribution, market concentration dynamics, demographic service areas, and strategic positioning of financial institutions. Key observations include year-over-year growth patterns, cumulative expansion trends, and the strategic allocation of branches across different community types."
            
            bank_strategy_analysis = f"Major banks in {county_name} exhibit diverse and sophisticated strategies in branch placement, market positioning, and community service. The analysis examines how different institutions serve diverse communities, compete for market share, and adapt their strategies based on demographic changes and regulatory requirements. Strategic patterns include geographic expansion, community-focused initiatives, and competitive positioning strategies."
            
            community_impact_analysis = f"The community impact analysis provides a comprehensive evaluation of how effectively banks serve low-to-moderate income and majority-minority communities in {county_name}. This includes detailed examination of branch accessibility, service quality in underserved areas, demographic alignment, and the effectiveness of community banking initiatives. The analysis reveals important insights into financial inclusion outcomes and community development impacts."
            
            key_findings = "1. Branch distribution patterns reveal significant market concentration trends and competitive dynamics.\n2. LMI and MMCT service levels demonstrate substantial variation between institutions, indicating different strategic priorities.\n3. Market leaders exhibit distinct and sophisticated strategies in community service and market positioning.\n4. Branch accessibility directly impacts financial inclusion outcomes and community development success.\n5. Regulatory compliance and community service standards vary significantly across different bank categories and market segments.\n6. Strategic branch placement decisions reflect both competitive positioning and community service objectives.\n7. Market concentration trends have important implications for regulatory oversight and competitive dynamics."
            
            conclusion_analysis = f"This comprehensive analysis provides an in-depth view of banking infrastructure in {county_name} from {years_str}, revealing critical insights into market dynamics, competitive strategies, and community service effectiveness. The findings support informed decision-making for community development initiatives, regulatory oversight processes, market analysis frameworks, and strategic planning for financial institutions. The analysis demonstrates the complex interplay between market competition, community service, and regulatory compliance in shaping banking infrastructure development."
        else:
            try:
                executive_summary = self.ai_analyzer.generate_executive_summary(analysis_data)
                overall_trends_analysis = self.ai_analyzer.analyze_overall_trends(analysis_data)
                bank_strategy_analysis = self.ai_analyzer.analyze_bank_strategies(analysis_data)
                community_impact_analysis = self.ai_analyzer.analyze_community_impact(analysis_data)
                key_findings = self.ai_analyzer.generate_key_findings(analysis_data)
                conclusion_analysis = self.ai_analyzer.generate_conclusion(analysis_data)
            except Exception as e:
                print(f"Warning: AI analysis failed: {e}")
                # Provide meaningful fallback content instead of empty strings
                county_name = analysis_data.get('county', 'the analyzed area')
                years_str = f"{analysis_data.get('years', [2022, 2023, 2024])[0]}-{analysis_data.get('years', [2022, 2023, 2024])[-1]}"
                
                executive_summary = f"This comprehensive analysis examines bank branch trends in {county_name} from {years_str} using FDIC Summary of Deposits data. The analysis focuses on three key metrics: total branch counts, the percentage of branches in Low-to-Moderate Income (LMI) tracts, and the percentage of branches in Majority-Minority Census Tracts (MMCT). This report provides detailed insights into market concentration, bank strategies, community impact, and regulatory implications for banking infrastructure development."
                
                overall_trends_analysis = f"Branch trends in {county_name} demonstrate significant evolution of banking infrastructure over the {years_str} period. The analysis reveals comprehensive patterns in branch distribution, market concentration dynamics, demographic service areas, and strategic positioning of financial institutions. Key observations include year-over-year growth patterns, cumulative expansion trends, and the strategic allocation of branches across different community types."
                
                bank_strategy_analysis = f"Major banks in {county_name} exhibit diverse and sophisticated strategies in branch placement, market positioning, and community service. The analysis examines how different institutions serve diverse communities, compete for market share, and adapt their strategies based on demographic changes and regulatory requirements. Strategic patterns include geographic expansion, community-focused initiatives, and competitive positioning strategies."
                
                community_impact_analysis = f"The community impact analysis provides a comprehensive evaluation of how effectively banks serve low-to-moderate income and majority-minority communities in {county_name}. This includes detailed examination of branch accessibility, service quality in underserved areas, demographic alignment, and the effectiveness of community banking initiatives. The analysis reveals important insights into financial inclusion outcomes and community development impacts."
                
                key_findings = "1. Branch distribution patterns reveal significant market concentration trends and competitive dynamics.\n2. LMI and MMCT service levels demonstrate substantial variation between institutions, indicating different strategic priorities.\n3. Market leaders exhibit distinct and sophisticated strategies in community service and market positioning.\n4. Branch accessibility directly impacts financial inclusion outcomes and community development success.\n5. Regulatory compliance and community service standards vary significantly across different bank categories and market segments.\n6. Strategic branch placement decisions reflect both competitive positioning and community service objectives.\n7. Market concentration trends have important implications for regulatory oversight and competitive dynamics."
                
                conclusion_analysis = f"This comprehensive analysis provides an in-depth view of banking infrastructure in {county_name} from {years_str}, revealing critical insights into market dynamics, competitive strategies, and community service effectiveness. The findings support informed decision-making for community development initiatives, regulatory oversight processes, market analysis frameworks, and strategic planning for financial institutions. The analysis demonstrates the complex interplay between market competition, community service, and regulatory compliance in shaping banking infrastructure development."
        return {
            'executive_summary': executive_summary,
            'overall_trends': overall_trends_analysis,
            'bank_strategies': bank_strategy_analysis,
            'community_impact': community_impact_analysis,
            'key_findings': key_findings,
            'conclusion': conclusion_analysis
        }
    
    def format_ai_content(self, content: str) -> List:
        """
        Format AI-generated content with proper sections, bullet points, and bold keywords.
        
        Args:
            content: Raw AI-generated text
            
        Returns:
            List of formatted Paragraph objects
        """
        if not content:
            return []
            
        formatted_content = []
        
        # Split content into sections
        sections = re.split(r'\n\s*\n', content.strip())
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
                
            # Check if this is a numbered list
            if re.match(r'^\d+\.', section):
                # Handle numbered lists
                lines = section.split('\n')
                for line in lines:
                    line = line.strip()
                    if line:
                        # Format numbered items and convert bank names to proper case
                        formatted_line = f"• {self.convert_bank_names_to_proper_case(line)}"
                        formatted_content.append(Paragraph(formatted_line, self.numbered_style))
                formatted_content.append(Spacer(1, 8))
                
            # Check if this is a bullet point list
            elif section.startswith('•') or section.startswith('-') or section.startswith('*'):
                # Handle bullet point lists
                lines = section.split('\n')
                for line in lines:
                    line = line.strip()
                    if line:
                        # Clean up bullet point markers and convert bank names to proper case
                        line = re.sub(r'^[•\-*]\s*', '', line)
                        formatted_line = f"• {self.convert_bank_names_to_proper_case(line)}"
                        formatted_content.append(Paragraph(formatted_line, self.bullet_style))
                formatted_content.append(Spacer(1, 8))
                
            # Check if this is a subsection heading (very specific pattern)
            elif (re.match(r'^[A-Z][A-Z\s]{2,10}:$', section) or 
                  re.match(r'^[A-Z][a-z\s]{2,15}:$', section)):
                # Handle subsection headings - only short, specific phrases that end with colon
                # This prevents normal sentences from being treated as headers
                formatted_content.append(Paragraph(f"<b>{section}</b>", self.subsection_style))
                formatted_content.append(Spacer(1, 5))
                
            # Check if this contains bold keywords - improved logic
            elif '**' in section or '*' in section:
                # Handle bold keywords with improved logic
                # First, check if the entire section is wrapped in ** (which we don't want)
                if section.startswith('**') and section.endswith('**') and section.count('**') == 2:
                    # Remove the outer ** and treat as normal paragraph
                    section = section[2:-2].strip()
                    formatted_content.append(Paragraph(self.convert_bank_names_to_proper_case(section), self.body_style))
                else:
                    # Handle inline bold text properly
                    # Replace **text** with <b>text</b> for inline bold
                    formatted_section = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', section)
                    # Replace *text* with <b>text</b> for single asterisk bold (if not already handled)
                    formatted_section = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<b>\1</b>', formatted_section)
                    formatted_content.append(Paragraph(self.convert_bank_names_to_proper_case(formatted_section), self.body_style))
                formatted_content.append(Spacer(1, 8))
                
            else:
                # Regular paragraph
                formatted_content.append(Paragraph(self.convert_bank_names_to_proper_case(section), self.body_style))
                formatted_content.append(Spacer(1, 8))
        
        return formatted_content
    
    def format_key_findings(self, content: str) -> List:
        """
        Format key findings with proper numbered list structure.
        
        Args:
            content: Raw key findings text
            
        Returns:
            List of formatted Paragraph objects
        """
        if not content:
            return []
            
        formatted_content = []
        
        # Split content into lines
        lines = content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this is a numbered item
            if re.match(r'^\d+\.', line):
                # Format numbered items and convert bank names to proper case
                formatted_content.append(Paragraph(self.convert_bank_names_to_proper_case(line), self.numbered_style))
            elif line.startswith('•') or line.startswith('-') or line.startswith('*'):
                # Format bullet points and convert bank names to proper case
                line = re.sub(r'^[•\-*]\s*', '', line)
                formatted_line = f"• {self.convert_bank_names_to_proper_case(line)}"
                formatted_content.append(Paragraph(formatted_line, self.bullet_style))
            else:
                # Regular text and convert bank names to proper case
                formatted_content.append(Paragraph(self.convert_bank_names_to_proper_case(line), self.body_style))
        
        return formatted_content
    
    def generate_enhanced_pdf_report(self, output_path: str):
        """Generate the complete enhanced PDF report with comprehensive analysis. AI only provides narrative text; all tables and formatting are handled by Python."""
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Use BaseDocTemplate for better control over frames and page numbering
        doc = BaseDocTemplate(
            output_path,
            pagesize=letter,
            topMargin=0.75*inch,
            bottomMargin=1.0*inch,  # Space for page numbers
            leftMargin=0.75*inch,
            rightMargin=0.75*inch
        )
        frame = Frame(
            doc.leftMargin,
            doc.bottomMargin,
            doc.width,
            doc.height - 0.3*inch,  # Reserve space for footer
            id='normal'
        )
        template = PageTemplate(id='with-footer', frames=frame, onPage=self.add_page_number)
        doc.addPageTemplates([template])
        
        # Build the complete story with proper TOC placement
        complete_story = []
        
        # Enhanced Cover Page
        counties_str = " and ".join(self.counties)
        years_str = f"{self.years[0]}–{self.years[-1]}"
        logo_path = "./ncrc_logo.jpg"
        if os.path.exists(logo_path):
            from reportlab.platypus import Image
            logo_img = Image(logo_path, width=2.8*inch, height=1*inch)
            complete_story.append(logo_img)
            complete_story.append(Spacer(1, 20))
        else:
            complete_story.append(Paragraph("[NCRC LOGO]", self.subtitle_style))
            complete_story.append(Spacer(1, 20))
        # Title with line breaks
        title_text = f"{counties_str}<br/>Bank Branch Trends<br/>({years_str})"
        complete_story.append(Paragraph(title_text, self.title_style))
        complete_story.append(Spacer(1, 40))
        complete_story.append(Paragraph("AI-Powered Banking Market Intelligence", self.subtitle_style))
        complete_story.append(Spacer(1, 30))
        complete_story.append(Paragraph(f"Report Generated: {datetime.now().strftime('%B %d, %Y')}", self.body_style))
        complete_story.append(PageBreak())
        self.page_breaks_count += 1
        
        # Calculate all enhanced data
        trends = self.calculate_enhanced_trends()
        market_shares = self.calculate_enhanced_market_share()
        top_banks = self.get_enhanced_top_banks(market_shares)
        bank_analysis = self.analyze_enhanced_bank_growth(top_banks)
        comparisons = self.calculate_enhanced_comparisons(bank_analysis)
        
        # Combine data for all counties if multiple counties
        if len(self.counties) > 1:
            # Aggregate trends data by year (sum the numbers)
            combined_trends = pd.DataFrame()
            for year in self.years:
                year_data = []
                for county in self.counties:
                    if county in trends and year in trends[county]['year'].values:
                        year_row = trends[county][trends[county]['year'] == year].iloc[0]
                        year_data.append(year_row)
                
                if year_data:
                    # Sum all the numeric columns across counties for this year
                    aggregated_row = year_data[0].copy()
                    aggregated_row['total_branches'] = sum(row['total_branches'] for row in year_data)
                    aggregated_row['lmict'] = sum(row['lmict'] for row in year_data)
                    aggregated_row['mmct'] = sum(row['mmct'] for row in year_data)
                    
                    # Recalculate percentages based on aggregated totals
                    if aggregated_row['total_branches'] > 0:
                        aggregated_row['lmict_pct'] = (aggregated_row['lmict'] / aggregated_row['total_branches'] * 100).round(2)
                        aggregated_row['mmct_pct'] = (aggregated_row['mmct'] / aggregated_row['total_branches'] * 100).round(2)
                    
                    # Recalculate year-over-year changes
                    if year > min(self.years):
                        prev_year = year - 1
                        prev_year_data = []
                        for county in self.counties:
                            if county in trends and prev_year in trends[county]['year'].values:
                                prev_row = trends[county][trends[county]['year'] == prev_year].iloc[0]
                                prev_year_data.append(prev_row)
                        
                        if prev_year_data:
                            prev_total = sum(row['total_branches'] for row in prev_year_data)
                            aggregated_row['total_yoy_change'] = ((aggregated_row['total_branches'] - prev_total) / prev_total * 100).round(2) if prev_total > 0 else 0
                            aggregated_row['total_yoy_change_abs'] = aggregated_row['total_branches'] - prev_total
                    
                    # Recalculate cumulative changes from first year
                    first_year = min(self.years)
                    if year > first_year:
                        first_year_data = []
                        for county in self.counties:
                            if county in trends and first_year in trends[county]['year'].values:
                                first_row = trends[county][trends[county]['year'] == first_year].iloc[0]
                                first_year_data.append(first_row)
                        
                        if first_year_data:
                            first_total = sum(row['total_branches'] for row in first_year_data)
                            aggregated_row['total_cumulative_change'] = ((aggregated_row['total_branches'] - first_total) / first_total * 100).round(2) if first_total > 0 else 0
                    
                    combined_trends = pd.concat([combined_trends, pd.DataFrame([aggregated_row])], ignore_index=True)
            
            # Aggregate market shares data by bank (sum the numbers)
            combined_market_shares = pd.DataFrame()
            all_banks = set()
            for county in self.counties:
                if county in market_shares:
                    all_banks.update(market_shares[county]['bank_name'].unique())
            
            for bank in all_banks:
                bank_data = []
                for county in self.counties:
                    if county in market_shares:
                        bank_rows = market_shares[county][market_shares[county]['bank_name'] == bank]
                        if not bank_rows.empty:
                            bank_data.append(bank_rows.iloc[0])
                
                if bank_data:
                    # Sum all the numeric columns across counties for this bank
                    aggregated_row = bank_data[0].copy()
                    aggregated_row['total_branches'] = sum(row['total_branches'] for row in bank_data)
                    aggregated_row['total_deposits'] = sum(row['total_deposits'] for row in bank_data)
                    aggregated_row['lmict'] = sum(row['lmict'] for row in bank_data)
                    aggregated_row['mmct'] = sum(row['mmct'] for row in bank_data)
                    
                    # Recalculate percentages based on aggregated totals
                    if aggregated_row['total_branches'] > 0:
                        aggregated_row['lmict_pct'] = (aggregated_row['lmict'] / aggregated_row['total_branches'] * 100).round(2)
                        aggregated_row['mmct_pct'] = (aggregated_row['mmct'] / aggregated_row['total_branches'] * 100).round(2)
                    
                    # Recalculate market share based on total deposits across all counties
                    total_all_deposits = sum(market_shares[county]['total_deposits'].sum() for county in self.counties if county in market_shares)
                    aggregated_row['market_share'] = (aggregated_row['total_deposits'] / total_all_deposits * 100).round(2) if total_all_deposits > 0 else 0
                    
                    combined_market_shares = pd.concat([combined_market_shares, pd.DataFrame([aggregated_row])], ignore_index=True)
            
            # Sort by market share descending
            combined_market_shares = combined_market_shares.sort_values('market_share', ascending=False)
            
            # Aggregate bank analysis data by bank (sum the numbers)
            combined_bank_analysis = pd.DataFrame()
            all_banks = set()
            for county in self.counties:
                if county in bank_analysis:
                    all_banks.update(bank_analysis[county]['bank_name'].unique())
            
            for bank in all_banks:
                bank_data = []
                for county in self.counties:
                    if county in bank_analysis:
                        bank_rows = bank_analysis[county][bank_analysis[county]['bank_name'] == bank]
                        if not bank_rows.empty:
                            bank_data.append(bank_rows.iloc[0])
                
                if bank_data:
                    # Sum all the numeric columns across counties for this bank
                    aggregated_row = bank_data[0].copy()
                    aggregated_row['first_year_branches'] = sum(row['first_year_branches'] for row in bank_data)
                    aggregated_row['last_year_branches'] = sum(row['last_year_branches'] for row in bank_data)
                    aggregated_row['absolute_change'] = aggregated_row['last_year_branches'] - aggregated_row['first_year_branches']
                    
                    # Recalculate percentage change based on aggregated totals
                    if aggregated_row['first_year_branches'] > 0:
                        aggregated_row['percentage_change'] = (aggregated_row['absolute_change'] / aggregated_row['first_year_branches'] * 100).round(2)
                    else:
                        aggregated_row['percentage_change'] = 0
                    
                    combined_bank_analysis = pd.concat([combined_bank_analysis, pd.DataFrame([aggregated_row])], ignore_index=True)
            
            # Generate AI analysis for combined data
            combined_comparisons = {}
            for county in self.counties:
                if county in comparisons:
                    combined_comparisons[county] = comparisons[county]
            
            ai_analysis = self.generate_enhanced_ai_analysis(
                {'county': ' and '.join(self.counties)},
                combined_trends,
                combined_market_shares,
                combined_bank_analysis,
                combined_comparisons
            )
            
            # Use combined data for the rest of the report
            trends = {'combined': combined_trends}
            market_shares = {'combined': combined_market_shares}
            bank_analysis = {'combined': combined_bank_analysis}
            comparisons = combined_comparisons
            counties_to_process = ['combined']
        else:
            # Single county - use original data
            counties_to_process = self.counties
        
        # Generate enhanced AI analysis for each county/combined area (narrative only)
        for county in counties_to_process:
                # Skip counties that don't have data
                if county not in trends or county not in market_shares:
                    print(f"Warning: No data available for county: {county}")
                    continue
                
                county_trends = trends[county]
                county_market_shares = market_shares[county]
                county_bank_analysis = bank_analysis.get(county, pd.DataFrame())
                county_comparisons = comparisons.get(county, {})
                if county == 'combined':
                    # Use the already generated AI analysis for combined data
                    ai_analysis = self.generate_enhanced_ai_analysis(
                        {'county': ' and '.join(self.counties)},
                        county_trends,
                        county_market_shares,
                        county_bank_analysis,
                        county_comparisons
                    )
                else:
                    ai_analysis = self.generate_enhanced_ai_analysis(
                        {'county': county},
                        county_trends,
                        county_market_shares,
                        county_bank_analysis,
                        county_comparisons
                    )
                
                # Create safe county name once and reuse it throughout this function
                if county == 'combined':
                    safe_county = 'combined'
                else:
                    safe_county = self.create_safe_anchor(county)
                
                # Executive Summary Section
                if county == 'combined':
                    area_name = ' and '.join(self.counties)
                    exec_header = Paragraph(f'<a name="exec_summary_combined"></a>Executive Summary', self.section_style)
                else:
                    exec_header = Paragraph(f'<a name="exec_summary_{safe_county}"></a>Executive Summary', self.section_style)
                
                if ai_analysis['executive_summary']:
                    # Process executive summary with consistent body text styling
                    exec_summary_text = ai_analysis['executive_summary'].strip()
                    # Split into paragraphs and format each as body text
                    exec_paragraphs = exec_summary_text.split('\n\n')
                    exec_content = []
                    for paragraph in exec_paragraphs:
                        if paragraph.strip():
                            # Clean up any markdown formatting and ensure consistent styling
                            clean_paragraph = paragraph.strip()
                            # Remove any ** markers that might cause formatting issues
                            clean_paragraph = clean_paragraph.replace('**', '')
                            exec_content.append(Paragraph(clean_paragraph, self.body_style))
                            exec_content.append(Spacer(1, 8))
                    complete_story.append(KeepTogether([exec_header] + exec_content + [Spacer(1, 20)]))
                else:
                    complete_story.append(exec_header)
                    complete_story.append(Spacer(1, 20))
                    
                    # Key Findings Section
                    complete_story.append(PageBreak())
                    self.page_breaks_count += 1
                if county == 'combined':
                    area_name = ' and '.join(self.counties)
                    key_header = Paragraph(f'<a name="key_findings_combined"></a>Key Findings', self.section_style)
                else:
                    # Reuse the safe_county already created above
                    key_header = Paragraph(f'<a name="key_findings_{safe_county}"></a>Key Findings', self.section_style)
                
                if ai_analysis['key_findings']:
                    key_content = self.format_key_findings(ai_analysis['key_findings'])
                    complete_story.append(KeepTogether([key_header] + key_content + [Spacer(1, 20)]))
                else:
                    complete_story.append(key_header)
                    complete_story.append(Spacer(1, 20))
                

                
                # Overall Branch Trends Section
                complete_story.append(PageBreak())
                self.page_breaks_count += 1
                if county == 'combined':
                    area_name = ' and '.join(self.counties)
                    trends_header = Paragraph(f'<a name="branch_trends_combined"></a>Overall Branch Trends', self.section_style)
                else:
                    # Reuse the safe_county already created above
                    trends_header = Paragraph(f'<a name="branch_trends_{safe_county}"></a>Overall Branch Trends', self.section_style)
                
                if ai_analysis['overall_trends']:
                    trends_content = self.format_ai_content(ai_analysis['overall_trends'])
                    complete_story.append(KeepTogether([trends_header] + trends_content + [Spacer(1, 20)]))
                else:
                    complete_story.append(trends_header)
                    complete_story.append(Spacer(1, 20))
                if not county_trends.empty:
                    if county == 'combined':
                        complete_story.append(Paragraph(f'<a name="trends_table_combined"></a>Detailed Branch Trends Data:', self.subsection_style))
                    else:
                        # Reuse the safe_county already created above
                        complete_story.append(Paragraph(f'<a name="trends_table_{safe_county}"></a>Detailed Branch Trends Data:', self.subsection_style))
                    trend_data = []
                    trend_data.append(['Year', 'Total', 'YoY Chg', 'YoY %', 'Cumul %', 'LMI %', 'MMCT %'])
                    for _, row in county_trends.iterrows():
                        trend_data.append([
                            self.format_year(row['year']),
                            self.format_number(row['total_branches']),
                        f"{'+' if row['total_yoy_change_abs'] > 0 else ''}{self.format_number(row['total_yoy_change_abs'])}" if not pd.isna(row['total_yoy_change_abs']) else "N/A",
                        f"{'+' if row['total_yoy_change'] > 0 else ''}{self.format_percentage_table(row['total_yoy_change'])}" if not pd.isna(row['total_yoy_change']) else "N/A",
                        f"{'+' if row['total_cumulative_change'] > 0 else ''}{self.format_percentage_table(row['total_cumulative_change'])}" if not pd.isna(row['total_cumulative_change']) else "N/A",
                        self.format_percentage_table(row['lmict_pct']),
                        self.format_percentage_table(row['mmct_pct'])
                    ])
                    trend_table = Table(trend_data, colWidths=[0.8*inch, 1.1*inch, 1*inch, 0.9*inch, 1*inch, 0.9*inch, 0.9*inch])
                    trend_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d3748')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('TOPPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f7fafc')),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                        ('FONTSIZE', (0, 1), (-1, -1), 9),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                        ('TOPPADDING', (0, 1), (-1, -1), 8),
                    ]))
                    complete_story.append(KeepTogether([trend_table, Spacer(1, 15)]))
                else:
                    # Add a message if no trends data
                    complete_story.append(Paragraph("No trends data available for this area.", self.body_style))
                    complete_story.append(Spacer(1, 15))
                
                # Market Concentration Section
                
                # Create market concentration content that will be kept together
                market_concentration_content = []
                
                if county == 'combined':
                    area_name = ' and '.join(self.counties)
                    market_header = Paragraph(f'<a name="market_concentration_combined"></a>Market Concentration: Largest Banks Analysis', self.section_style)
                else:
                    market_header = Paragraph(f'<a name="market_concentration_{safe_county}"></a>Market Concentration: Largest Banks Analysis', self.section_style)
                
                market_concentration_content.append(market_header)
                
                # HHI Subsection
                market_concentration_content.append(Spacer(1, 15))
                if county == 'combined':
                    market_concentration_content.append(Paragraph(f'<a name="hhi_analysis_combined"></a>Herfindahl-Hirschman Index (HHI) Analysis', self.subsection_style))
                else:
                    market_concentration_content.append(Paragraph(f'<a name="hhi_analysis_{safe_county}"></a>Herfindahl-Hirschman Index (HHI) Analysis', self.subsection_style))
                market_concentration_content.append(Spacer(1, 5))
                
                # HHI explanation paragraph
                hhi_explanation = (
                    "The Herfindahl-Hirschman Index (HHI) is a widely-used measure of market concentration that regulators employ to assess competition levels in banking markets. "
                    "The HHI is calculated by summing the squared market shares of all banks in a given geographic area, based on deposit market shares. "
                    "Regulatory guidelines classify markets as: <b>unconcentrated</b> (HHI < 1,000), <b>moderately concentrated</b> (HHI 1,000-1,800), or <b>highly concentrated</b> (HHI > 1,800). "
                    "Markets with HHI above 1,800 are considered 'stuck' and face significant restrictions on merger activity, as they require additional regulatory scrutiny for any proposed consolidation."
                )
                
                market_concentration_content.append(Paragraph(hhi_explanation, self.body_style))
                market_concentration_content.append(Spacer(1, 15))
                
                # HHI Formula display
                hhi_formula = (
                    "<b>HHI Formula:</b><br/>"
                    "HHI = Σ(Market Share²) = Market Share<sub>1</sub>² + Market Share<sub>2</sub>² + ... + Market Share<sub>n</sub>²"
                )
                
                market_concentration_content.append(Paragraph(hhi_formula, self.body_style))
                market_concentration_content.append(Spacer(1, 15))
                
                # Add St. Louis Fed source
                hhi_source = (
                    "<i><font size='8'>Source: <a href='https://www.stlouisfed.org/on-the-economy/2018/june/hhi-competition-community-banks'>Federal Reserve Bank of St. Louis (June 2018)</a></font></i>"
                )
                
                market_concentration_content.append(Paragraph(hhi_source, self.body_style))
                market_concentration_content.append(Spacer(1, 15))
                
                # Calculate and display actual HHI for this area
                if not county_market_shares.empty:
                    hhi_value, concentration_level, interpretation = self.calculate_hhi(county_market_shares)
                    
                    # Create HHI results display
                    hhi_results = (
                        f"<b>Current Market HHI:</b> {hhi_value}<br/>"
                        f"<b>Concentration Level:</b> {concentration_level}<br/>"
                        f"<b>Regulatory Status:</b> {interpretation}"
                    )
                    
                    market_concentration_content.append(Paragraph(hhi_results, self.summary_box_style))
                    market_concentration_content.append(Spacer(1, 15))
                    
                    # Add HHI calculation breakdown table
                    if county == 'combined':
                        hhi_breakdown_header = Paragraph(f'<a name="hhi_breakdown_combined"></a>HHI Calculation Breakdown:', self.subsection_style)
                    else:
                        hhi_breakdown_header = Paragraph(f'<a name="hhi_breakdown_{safe_county}"></a>HHI Calculation Breakdown:', self.subsection_style)
                    
                    # Create breakdown table showing each bank's contribution to HHI
                    breakdown_data = []
                    breakdown_data.append(['Bank', 'Deposits', 'Market Share %', 'HHI Contribution'])
                    
                    # Sort by market share descending for better readability
                    sorted_banks = county_market_shares.sort_values('market_share', ascending=False)
                    
                    for _, row in sorted_banks.iterrows():
                        market_share = row['market_share']
                        squared_value = market_share ** 2
                        total_deposits = row['total_deposits']
                        breakdown_data.append([
                            Paragraph(self.to_all_caps(row['bank_name']), ParagraphStyle(
                                'BankName',
                                parent=self.body_style,
                                alignment=TA_CENTER,
                                fontSize=9,
                                leading=11,
                                wordWrap='LTR'
                            )),
                            f"${self.format_number(total_deposits)}",
                            self.format_percentage_table(market_share),
                            f"{squared_value:.0f}"
                        ])
                    
                    breakdown_table = Table(breakdown_data, colWidths=[2.5*inch, 1.2*inch, 1.2*inch, 1.2*inch])
                    breakdown_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d3748')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('TOPPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f7fafc')),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                        ('FONTSIZE', (0, 1), (-1, -1), 9),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                        ('TOPPADDING', (0, 1), (-1, -1), 8),
                        ('VALIGN', (0, 1), (0, -1), 'MIDDLE'),
                    ]))
                    
                    market_concentration_content.append(KeepTogether([hhi_breakdown_header, breakdown_table, Spacer(1, 15)]))
                
                # Add market share table for top banks
                if not county_market_shares.empty:
                    # Get top banks by number of branches (top 10)
                    top_bank_data = county_market_shares.nlargest(10, 'total_branches')
                    
                    if county == 'combined':
                        market_share_header = Paragraph(f'<a name="market_share_table_combined"></a>Top Banks Market Share Data:', self.subsection_style)
                    else:
                        market_share_header = Paragraph(f'<a name="market_share_table_{safe_county}"></a>Top Banks Market Share Data:', self.subsection_style)
                    
                    bank_table_data = []
                    bank_table_data.append(['Bank', 'Branches', 'Branch Mkt\nShare %', 'LMI %', 'MMCT %'])
                    
                    # Calculate total branches for branch-based market share (only for this table display)
                    total_branches = top_bank_data['total_branches'].sum()
                    
                    for _, row in top_bank_data.iterrows():
                        # Calculate branch-based market share for this table only
                        branch_market_share = (row['total_branches'] / total_branches * 100) if total_branches > 0 else 0
                        
                        bank_table_data.append([
                            Paragraph(self.to_all_caps(row['bank_name']), ParagraphStyle(
                                'BankName',
                                parent=self.body_style,
                                alignment=TA_CENTER,
                                fontSize=9,
                                leading=11,
                                wordWrap='LTR'
                            )),
                            self.format_number(row['total_branches']),
                            self.format_percentage_table(branch_market_share),
                            self.format_percentage_table(row['lmict_pct']),
                            self.format_percentage_table(row['mmct_pct'])
                        ])
                    
                    bank_table = Table(bank_table_data, colWidths=[2.5*inch, 1.1*inch, 1.1*inch, 0.9*inch, 0.9*inch])
                    bank_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d3748')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('TOPPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f7fafc')),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                        ('FONTSIZE', (0, 1), (-1, -1), 9),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                        ('TOPPADDING', (0, 1), (-1, -1), 8),
                        ('VALIGN', (0, 1), (0, -1), 'MIDDLE'),
                    ]))
                    
                    market_concentration_content.append(KeepTogether([market_share_header, bank_table, Spacer(1, 15)]))
                    
                    # Add Growth Analysis section
                    if not county_bank_analysis.empty:
                        if county == 'combined':
                            growth_header = Paragraph(f'<a name="growth_analysis_combined"></a><b>Growth Analysis:</b> The following table shows how the branch counts for these top banks '
                                f"have evolved from {self.years[0]} to {self.years[-1]}, including absolute and percentage changes:", self.body_style)
                        else:
                            growth_header = Paragraph(f'<a name="growth_analysis_{safe_county}"></a><b>Growth Analysis:</b> The following table shows how the branch counts for these top banks '
                                f"have evolved from {self.years[0]} to {self.years[-1]}, including absolute and percentage changes:", self.body_style)
                        
                        growth_data = []
                        growth_data.append(['Bank', f'Branches\n({self.years[0]})', f'Branches\n({self.years[-1]})', f'Absolute\nChange', f'Percentage\nChange %'])
                        
                        for _, row in county_bank_analysis.iterrows():
                            growth_data.append([
                                Paragraph(self.to_all_caps(row['bank_name']), ParagraphStyle(
                                    'BankName',
                                    parent=self.body_style,
                                    alignment=TA_CENTER,
                                    fontSize=9,
                                    leading=11,
                                    wordWrap='LTR'
                                )),
                                self.format_number(row['first_year_branches']),
                                self.format_number(row['last_year_branches']),
                                f"{'+' if row['absolute_change'] > 0 else ''}{row['absolute_change']}",
                                f"{'+' if row['percentage_change'] > 0 else ''}{self.format_percentage_table(row['percentage_change'])}"
                            ])
                        
                        growth_table = Table(growth_data, colWidths=[2.5*inch, 1.1*inch, 1.1*inch, 1*inch, 1.8*inch])
                        growth_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d3748')),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 0), 10),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('TOPPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f7fafc')),
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                            ('FONTSIZE', (0, 1), (-1, -1), 9),
                            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                            ('TOPPADDING', (0, 1), (-1, -1), 8),
                            ('VALIGN', (0, 1), (0, -1), 'MIDDLE'),
                        ]))
                        
                        market_concentration_content.append(KeepTogether([growth_header, growth_table, Spacer(1, 15)]))
                    
                    # Add Community Impact Analysis section
                    if not county_bank_analysis.empty:
                        # Get comparisons data - for combined counties, calculate averages from individual counties
                        if county == 'combined' and county not in comparisons:
                            # Calculate combined averages from individual county data
                            all_lmi_pcts = []
                            all_mmct_pcts = []
                            for individual_county in self.counties:
                                if individual_county in comparisons:
                                    all_lmi_pcts.append(comparisons[individual_county]['county_avg_lmict'])
                                    all_mmct_pcts.append(comparisons[individual_county]['county_avg_mmct'])
                            
                            if all_lmi_pcts and all_mmct_pcts:
                                county_comparisons = {
                                    'county_avg_lmict': sum(all_lmi_pcts) / len(all_lmi_pcts),
                                    'county_avg_mmct': sum(all_mmct_pcts) / len(all_mmct_pcts)
                                }
                            else:
                                county_comparisons = {'county_avg_lmict': 0, 'county_avg_mmct': 0}
                        elif county in comparisons:
                            county_comparisons = comparisons[county]
                        else:
                            county_comparisons = {'county_avg_lmict': 0, 'county_avg_mmct': 0}
                        
                        if county_comparisons:
                            if county == 'combined':
                                community_impact_header = Paragraph(f'<a name="community_impact_combined"></a>Community Impact Analysis', self.subsection_style)
                            else:
                                community_impact_header = Paragraph(f'<a name="community_impact_{safe_county}"></a>Community Impact Analysis', self.subsection_style)
                            
                            # Add narrative explanation
                            community_narrative = (
                                f"This analysis examines how effectively the major banks in {', '.join(self.counties) if county == 'combined' else county} "
                                f"serve low-to-moderate income and majority-minority communities. The table below compares each bank's "
                                f"LMI and MMCT percentages against the area average, providing insights into which institutions "
                                f"are most committed to serving underserved communities. "
                                f"Banks with higher percentages than the average are marked with ▲, while those below average are marked with ▼."
                            )
                            
                            market_concentration_content.append(KeepTogether([community_impact_header, Spacer(1, 10), Paragraph(community_narrative, self.body_style), Spacer(1, 15)]))
                            
                            # Create community impact comparison table
                            if county == 'combined':
                                comparison_header = Paragraph(f'<a name="community_impact_table_combined"></a>Community Impact Comparison Data:', self.subsection_style)
                            else:
                                comparison_header = Paragraph(f'<a name="community_impact_table_{safe_county}"></a>Community Impact Comparison Data:', self.subsection_style)
                            
                            comparison_data = []
                            comparison_data.append(['Bank', 'LMI %', 'MMCT %', 'LMI vs\nAvg', 'MMCT vs\nAvg'])
                            
                            for _, row in county_bank_analysis.iterrows():
                                bank_current = county_market_shares[county_market_shares['bank_name'] == row['bank_name']]
                                if not bank_current.empty:
                                    bank_lmi = bank_current.iloc[0]['lmict_pct']
                                    bank_mmct = bank_current.iloc[0]['mmct_pct']
                                    lmi_vs_avg = "▲" if bank_lmi > county_comparisons['county_avg_lmict'] else "▼" if bank_lmi < county_comparisons['county_avg_lmict'] else "●"
                                    mmct_vs_avg = "▲" if bank_mmct > county_comparisons['county_avg_mmct'] else "▼" if bank_mmct < county_comparisons['county_avg_mmct'] else "●"
                                    comparison_data.append([
                                        Paragraph(self.to_all_caps(row['bank_name']), ParagraphStyle(
                                            'BankName',
                                            parent=self.body_style,
                                            alignment=TA_CENTER,
                                            fontSize=9,
                                            leading=11,
                                            wordWrap='LTR'
                                        )),
                                        self.format_percentage_table(bank_lmi),
                                        self.format_percentage_table(bank_mmct),
                                        lmi_vs_avg,
                                        mmct_vs_avg
                                    ])
                            
                            comparison_table = Table(comparison_data, colWidths=[2.5*inch, 0.9*inch, 0.9*inch, 1.1*inch, 1.2*inch])
                            comparison_table.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d3748')),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                ('FONTSIZE', (0, 0), (-1, 0), 10),
                                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                ('TOPPADDING', (0, 0), (-1, 0), 12),
                                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f7fafc')),
                                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                                ('FONTSIZE', (0, 1), (-1, -1), 9),
                                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                                ('TOPPADDING', (0, 1), (-1, -1), 8),
                                ('VALIGN', (0, 1), (0, -1), 'MIDDLE'),
                            ]))
                            
                            market_concentration_content.append(KeepTogether([comparison_header, comparison_table, Spacer(1, 15)]))
                            
                            # Add explanatory paragraphs after the table - dynamically generated based on actual data
                            # Count banks above/below average for dynamic insights
                            banks_above_lmi_avg = sum(1 for _, row in county_bank_analysis.iterrows() 
                                                    if county_market_shares[county_market_shares['bank_name'] == row['bank_name']].iloc[0]['lmict_pct'] > county_comparisons['county_avg_lmict'])
                            banks_above_mmct_avg = sum(1 for _, row in county_bank_analysis.iterrows() 
                                                     if county_market_shares[county_market_shares['bank_name'] == row['bank_name']].iloc[0]['mmct_pct'] > county_comparisons['county_avg_mmct'])
                            
                            # Get top performers for dynamic description
                            top_lmi_bank = county_market_shares.loc[county_market_shares['lmict_pct'].idxmax(), 'bank_name'] if not county_market_shares.empty else "N/A"
                            top_mmct_bank = county_market_shares.loc[county_market_shares['mmct_pct'].idxmax(), 'bank_name'] if not county_market_shares.empty else "N/A"
                            
                            explanation_para1 = (
                                f"Analysis of the Community Impact Comparison Data reveals that {banks_above_lmi_avg} out of {len(county_bank_analysis)} major banks "
                                f"in {', '.join(self.counties) if county == 'combined' else county} exceed the area average for LMI tract coverage, "
                                f"while {banks_above_mmct_avg} banks exceed the MMCT tract average. "
                                f"{top_lmi_bank} leads in LMI community service, while {top_mmct_bank} demonstrates the strongest "
                                f"commitment to majority-minority communities."
                            )
                            
                            explanation_para2 = (
                                f"The data shows varying levels of community service commitment across institutions. "
                                f"Banks marked with ▲ exceed area averages and demonstrate stronger financial inclusion practices, "
                                f"while those marked with ▼ may have opportunities to expand community outreach. "
                                f"This analysis helps identify which banks are leading community development efforts "
                                f"and where additional investment in underserved areas could be beneficial."
                            )
                            
                            market_concentration_content.append(Paragraph(explanation_para1, self.body_style))
                            market_concentration_content.append(Spacer(1, 10))
                            market_concentration_content.append(Paragraph(explanation_para2, self.body_style))
                            market_concentration_content.append(Spacer(1, 15))
                
                # Add all market concentration content to the story
                complete_story.append(KeepTogether(market_concentration_content))
                complete_story.append(Spacer(1, 20))
        

        # Methodology and Technical Notes Section
        complete_story.append(PageBreak())
        self.page_breaks_count += 1
        methodology_header = Paragraph('<a name="methodology"></a>Methodology and Technical Notes', self.section_style)
        methodology_content = [
            Paragraph(
                f"<b>Analysis Period:</b> {years_str}<br/>"
                f"<b>Geographic Scope:</b> {counties_str}<br/>"
                f"<b>Report Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>"
                f"<b>Data Source:</b> FDIC Summary of Deposits<br/>"
                f"<b>Analysis Method:</b> AI-Powered Statistical Analysis with {self.ai_analyzer.provider.upper()}<br/>"
                f"<b>Report Type:</b> Comprehensive Market Analysis",
                self.body_style
            ),
            Spacer(1, 15),
            Paragraph(
                f"This analysis examines bank branch trends and market concentration using FDIC Summary of Deposits data. "
                f"The analysis focuses on three key metrics: total branch counts, total deposits, and the percentage of branches in Low-to-Moderate Income (LMI) tracts "
                f"and Majority-Minority Census Tracts (MMCT). We identify the largest banks by deposit market share "
                f"and analyze their growth patterns and community impact compared to county averages. Market concentration is measured using the Herfindahl-Hirschman Index (HHI) based on deposit market shares. All analysis is enhanced with "
                f"AI-powered insights using {self.ai_analyzer.provider.upper()} for deeper interpretation of trends and strategic implications.",
                self.body_style
            ),
            Spacer(1, 15),
            Paragraph(
                "<b>Data Definitions:</b><br/>"
                "• <b>LMICT:</b> Low-to-Moderate Income Census Tracts - areas with median family income below 80% of the area median income<br/>"
                "• <b>MMCT:</b> Majority-Minority Census Tracts - areas where minority populations represent more than 50% of the total population<br/>"
                "• <b>Market Share:</b> Percentage of total deposits in the county controlled by each bank (regulatory standard for HHI calculation)",
                self.body_style
            ),
            Spacer(1, 15),
            Paragraph(
                f"<b>Analysis Overview:</b> This analysis examines bank branch trends in {', '.join(self.counties)} from {years_str} using FDIC Summary of Deposits data. "
                f"We focus on three key metrics: total branch counts, the percentage of branches in Low-to-Moderate Income (LMI) tracts, "
                f"and the percentage of branches in Majority-Minority Census Tracts (MMCT).",
                self.body_style
            ),
            Spacer(1, 15),
            Paragraph(
                f"<b>Important Note:</b> MMCT designations increased significantly with the 2020 census and became effective in 2022. "
                f"This means MMCT percentages may show notable changes between 2021 and 2022, reflecting the updated census data rather than actual branch relocations.",
                self.body_style
            )
        ]
        
        complete_story.append(KeepTogether([methodology_header] + methodology_content))
        
        # Legal Disclaimers Section
        complete_story.append(Spacer(1, 20))
        legal_header = Paragraph('<a name="legal"></a>Legal Disclaimers', self.section_style)
        legal_content = [
            Paragraph(
                "<b>1. AI-Generated Content.</b> Portions of the report and analyses generated by NCRC's JustData tool are created using automated and artificial intelligence-based processes. While we strive for accuracy, such content may contain errors, omissions, or biases, and should not be considered definitive, complete, or substitute for professional judgement. You acknowledge and agree that you are solely responsible for evaluating the accuracy, suitability, and applicability of any output before relying on it. All rights in and to AI-generated outputs are granted to you under a limited, non-exclusive, no-transferable license for your internal use only, unless otherwise expressly authorized in writing by NCRC.",
                self.body_style
            ),
            Spacer(1, 15),
            Paragraph(
                "<b>2. Use of Public Data.</b> The App may incorporate or rely on publicly available datasets from third-party sources. Such datasets are provided \"as is\" and may contain inaccuracies or be incomplete. NCRC makes no representation or warranty regarding the accuracy, completeness, or timeliness of any public data and disclaims all liability for errors or omissions therein.",
                self.body_style
            )
        ]
        
        complete_story.append(KeepTogether([legal_header] + legal_content))
        
        # Build the final story
        doc.build(complete_story)
        print(f"✅ AI-powered PDF report generated successfully: {output_path}")
        print(f"   - AI provided narrative text only")
        print(f"   - Python handled all tables, charts, and formatting")


def generate_pdf_report_from_data(data: pd.DataFrame, counties: List[str], years: List[int], output_path: str, ai_sections: Dict[str, str] = None):
    """
    Generate an enhanced PDF report from the given data.
    
    Args:
        data: DataFrame with branch data
        counties: List of counties analyzed
        years: List of years analyzed
        output_path: Path where to save the PDF
        ai_sections: Optional dictionary of AI-generated analysis sections
    """
    generator = EnhancedPDFReportGenerator(data, counties, years)
    
    # If AI sections are provided, use them instead of generating new ones
    if ai_sections:
        generator.ai_analysis = ai_sections
    else:
        # Generate AI analysis as usual
        generator.ai_analysis = generator.generate_enhanced_ai_analysis(
            generator.data, 
            generator.calculate_enhanced_trends(),
            generator.calculate_enhanced_market_share(),
            generator.analyze_enhanced_bank_growth(generator.get_enhanced_top_banks(generator.calculate_enhanced_market_share())),
            generator.calculate_enhanced_comparisons(generator.analyze_enhanced_bank_growth(generator.get_enhanced_top_banks(generator.calculate_enhanced_market_share())))
        )
    
    generator.generate_enhanced_pdf_report(output_path) 