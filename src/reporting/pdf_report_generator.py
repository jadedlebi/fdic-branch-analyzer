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


class TOCEntry:
    """Represents a table of contents entry with navigation information."""
    def __init__(self, title: str, level: int, page: int, anchor: str = None):
        self.title = title
        self.level = level  # 1 = section, 2 = subsection, 3 = sub-subsection
        self.page = page
        self.anchor = anchor or f"toc_{len(title)}".replace(" ", "_").replace(":", "").replace("(", "").replace(")", "")


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
        
        required_columns = ['bank_name', 'year', 'county_state', 'total_branches', 'lmict', 'mmct']
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
        self.ai_analyzer = AIAnalyzer()
        self.toc_entries = []  # Track table of contents entries
        self.current_page = 1  # Track current page number
        
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
        
        # TOC styles
        self.toc_title_style = ParagraphStyle(
            'TOCTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1a365d'),
            fontName='Helvetica-Bold',
            leading=28
        )
        
        self.toc_section_style = ParagraphStyle(
            'TOCSection',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=8,
            spaceBefore=15,
            textColor=colors.HexColor('#2d3748'),
            fontName='Helvetica-Bold',
            leading=14
        )
        
        self.toc_subsection_style = ParagraphStyle(
            'TOCSubsection',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            spaceBefore=8,
            leftIndent=20,
            textColor=colors.HexColor('#4a5568'),
            fontName='Helvetica',
            leading=12
        )
        
        self.toc_table_style = ParagraphStyle(
            'TOCTable',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=4,
            spaceBefore=4,
            leftIndent=40,
            textColor=colors.HexColor('#718096'),
            fontName='Helvetica',
            leading=11
        )

    def add_toc_entry(self, title: str, level: int, anchor: str = None):
        """Add a table of contents entry."""
        entry = TOCEntry(title, level, self.current_page, anchor)
        self.toc_entries.append(entry)
        
    def create_toc_page(self) -> List:
        """Create the table of contents page."""
        toc_story = []
        
        # TOC Title
        toc_story.append(Paragraph("Table of Contents", self.toc_title_style))
        toc_story.append(Spacer(1, 20))
        
        # Add TOC entries
        for entry in self.toc_entries:
            if entry.level == 1:  # Section
                # Create clickable link with page number
                link_text = f'<link href="#{entry.anchor}">{entry.title}</link> <i>Page {entry.page}</i>'
                toc_story.append(Paragraph(link_text, self.toc_section_style))
            elif entry.level == 2:  # Subsection
                link_text = f'<link href="#{entry.anchor}">{entry.title}</link> <i>Page {entry.page}</i>'
                toc_story.append(Paragraph(link_text, self.toc_subsection_style))
            elif entry.level == 3:  # Table/Figure
                link_text = f'<link href="#{entry.anchor}">{entry.title}</link> <i>Page {entry.page}</i>'
                toc_story.append(Paragraph(link_text, self.toc_table_style))
        
        return toc_story
    
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
                converted_text = converted_text.replace(bank_name, self.to_proper_case(bank_name))
        
        return converted_text
    
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
            # Calculate "Both %" as the minimum of LMI % and MMCT % (theoretical maximum overlap)
            # Since we don't have actual intersection data, this represents the maximum possible overlap
            yearly_stats['both_pct'] = np.minimum(yearly_stats['lmict_pct'], yearly_stats['mmct_pct']).round(2)
            
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
            
            # Calculate total branches in county
            total_county_branches = county_data['total_branches'].sum()
            
            # Calculate market share for each bank
            bank_stats = county_data.groupby('bank_name').agg({
                'total_branches': 'sum',
                'lmict': 'sum',
                'mmct': 'sum'
            }).reset_index()
            
            bank_stats['market_share'] = (bank_stats['total_branches'] / total_county_branches * 100).round(2) if total_county_branches > 0 else 0
            bank_stats['lmict_pct'] = np.where(bank_stats['total_branches'] > 0, 
                                              (bank_stats['lmict'] / bank_stats['total_branches'] * 100).round(2), 0)
            bank_stats['mmct_pct'] = np.where(bank_stats['total_branches'] > 0, 
                                             (bank_stats['mmct'] / bank_stats['total_branches'] * 100).round(2), 0)
            # Calculate "Both %" as the minimum of LMI % and MMCT % (theoretical maximum overlap)
            # Since we don't have actual intersection data, this represents the maximum possible overlap
            bank_stats['both_pct'] = np.minimum(bank_stats['lmict_pct'], bank_stats['mmct_pct']).round(2)
            
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
    
    def generate_enhanced_ai_analysis(self, county_data, trends, market_shares, bank_analysis, comparisons):
        """Generate enhanced AI-powered analysis using the configured AI provider for narrative insights only (no tables or formatting)."""
        # Prepare enhanced data for AI analysis
        analysis_data = {
            'county': county_data.get('county', 'Unknown County'),
            'years': self.years,
            'trends': trends.to_dict('records') if not trends.empty else [],
            'market_shares': market_shares.to_dict('records') if not market_shares.empty else [],
            'bank_analysis': bank_analysis.to_dict('records') if not bank_analysis.empty else [],
            'comparisons': comparisons
        }
        # Prompts are now explicit: only narrative, no tables or formatting
        try:
            executive_summary = self.ai_analyzer.generate_executive_summary(analysis_data)
            overall_trends_analysis = self.ai_analyzer.analyze_overall_trends(analysis_data)
            bank_strategy_analysis = self.ai_analyzer.analyze_bank_strategies(analysis_data)
            community_impact_analysis = self.ai_analyzer.analyze_community_impact(analysis_data)
            key_findings = self.ai_analyzer.generate_key_findings(analysis_data)
            conclusion_analysis = self.ai_analyzer.generate_conclusion(analysis_data)
        except Exception as e:
            print(f"Warning: AI analysis failed: {e}")
            # Provide fallback content
            executive_summary = ""
            overall_trends_analysis = ""
            bank_strategy_analysis = ""
            community_impact_analysis = ""
            key_findings = ""
            conclusion_analysis = ""
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
                
            # Check if this is a subsection heading
            elif re.match(r'^[A-Z][A-Z\s]+:', section) or re.match(r'^[A-Z][a-z\s]+:', section):
                # Handle subsection headings
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
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
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
        self.current_page += 1  # Cover page is page 1
        
        # Calculate all enhanced data
        trends = self.calculate_enhanced_trends()
        market_shares = self.calculate_enhanced_market_share()
        top_banks = self.get_enhanced_top_banks(market_shares)
        bank_analysis = self.analyze_enhanced_bank_growth(top_banks)
        comparisons = self.calculate_enhanced_comparisons(bank_analysis)
        
        # Combine data for all counties if multiple counties
        if len(self.counties) > 1:
            # Combine trends data
            combined_trends = pd.DataFrame()
            for county in self.counties:
                if county in trends:
                    county_trends = trends[county].copy()
                    county_trends['county'] = county
                    combined_trends = pd.concat([combined_trends, county_trends], ignore_index=True)
            
            # Combine market shares data
            combined_market_shares = pd.DataFrame()
            for county in self.counties:
                if county in market_shares:
                    county_market_shares = market_shares[county].copy()
                    county_market_shares['county'] = county
                    combined_market_shares = pd.concat([combined_market_shares, county_market_shares], ignore_index=True)
            
            # Combine bank analysis data
            combined_bank_analysis = pd.DataFrame()
            for county in self.counties:
                if county in bank_analysis:
                    county_bank_analysis = bank_analysis[county].copy()
                    county_bank_analysis['county'] = county
                    combined_bank_analysis = pd.concat([combined_bank_analysis, county_bank_analysis], ignore_index=True)
            
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
                pass
            else:
                ai_analysis = self.generate_enhanced_ai_analysis(
                    {'county': county},
                    county_trends,
                    county_market_shares,
                    county_bank_analysis,
                    county_comparisons
                )
            
            # Executive Summary Section
            complete_story.append(PageBreak())
            self.current_page += 1
            if county == 'combined':
                area_name = ' and '.join(self.counties)
                self.add_toc_entry(f"Executive Summary - {area_name}", 1, f"exec_summary_{county}")
                exec_header = Paragraph(f'<a name="exec_summary_{county}"></a>Executive Summary', self.section_style)
            else:
                self.add_toc_entry(f"Executive Summary - {county}", 1, f"exec_summary_{county}")
                exec_header = Paragraph(f'<a name="exec_summary_{county}"></a>Executive Summary', self.section_style)
            
            if ai_analysis['executive_summary']:
                exec_content = self.format_ai_content(ai_analysis['executive_summary'])
                complete_story.append(KeepTogether([exec_header] + exec_content + [Spacer(1, 20)]))
            else:
                complete_story.append(exec_header)
                complete_story.append(Spacer(1, 20))
                
            # Key Findings Section
            complete_story.append(PageBreak())
            self.current_page += 1
            if county == 'combined':
                area_name = ' and '.join(self.counties)
                self.add_toc_entry(f"Key Findings - {area_name}", 1, f"key_findings_{county}")
                complete_story.append(Paragraph(f'<a name="key_findings_{county}"></a>Key Findings', self.section_style))
            else:
                self.add_toc_entry(f"Key Findings - {county}", 1, f"key_findings_{county}")
                complete_story.append(Paragraph(f'<a name="key_findings_{county}"></a>Key Findings', self.section_style))
            if ai_analysis['key_findings']:
                key_content = self.format_key_findings(ai_analysis['key_findings'])
                complete_story.extend(key_content)
            complete_story.append(Spacer(1, 20))
            
            # Understanding the Data Section
            complete_story.append(PageBreak())
            self.current_page += 1
            if county == 'combined':
                area_name = ' and '.join(self.counties)
                self.add_toc_entry(f"Understanding the Data - {area_name}", 1, f"data_understanding_{county}")
                complete_story.append(Paragraph(f'<a name="data_understanding_{county}"></a>Understanding the Data', self.section_style))
                complete_story.append(Paragraph(
                    f"This analysis examines bank branch trends in {area_name} from {years_str} using FDIC Summary of Deposits data. "
                    f"We focus on three key metrics:",
                    self.body_style
                ))
            else:
                self.add_toc_entry(f"Understanding the Data - {county}", 1, f"data_understanding_{county}")
                data_header = Paragraph(f'<a name="data_understanding_{county}"></a>Understanding the Data', self.section_style)
                data_intro = Paragraph(
                    f"This analysis examines bank branch trends in {county} from {years_str} using FDIC Summary of Deposits data. "
                    f"We focus on three key metrics:",
                    self.body_style
                )
            
            data_bullets = [
                Paragraph("• <b>LMICT (Low-to-Moderate Income Census Tracts):</b> Branches located in areas with median family income below 80% of the area median income", self.bullet_style),
                Paragraph("• <b>MMCT (Majority-Minority Census Tracts):</b> Branches located in areas where minority populations represent more than 50% of the total population", self.bullet_style),
                Paragraph("• <b>LMI/MMCT:</b> Branches that serve both low-to-moderate income and majority-minority communities", self.bullet_style),
                Paragraph(
                    f"<b>Important Note:</b> MMCT designations increased significantly with the 2020 census and became effective in 2022. "
                    f"This means MMCT percentages may show notable changes between 2021 and 2022, reflecting the updated census data rather than actual branch relocations.",
                    self.body_style
                ),
                Spacer(1, 20)
            ]
            
            if county == 'combined':
                complete_story.append(KeepTogether([data_header, data_intro] + data_bullets))
            else:
                complete_story.append(KeepTogether([data_header, data_intro] + data_bullets))
            
            # Overall Branch Trends Section
            complete_story.append(PageBreak())
            self.current_page += 1
            if county == 'combined':
                area_name = ' and '.join(self.counties)
                self.add_toc_entry(f"Overall Branch Trends - {area_name}", 1, f"branch_trends_{county}")
                complete_story.append(Paragraph(f'<a name="branch_trends_{county}"></a>Overall Branch Trends', self.section_style))
            else:
                self.add_toc_entry(f"Overall Branch Trends - {county}", 1, f"branch_trends_{county}")
                trends_header = Paragraph(f'<a name="branch_trends_{county}"></a>Overall Branch Trends', self.section_style)
            
            if ai_analysis['overall_trends']:
                trends_content = self.format_ai_content(ai_analysis['overall_trends'])
                complete_story.append(KeepTogether([trends_header] + trends_content + [Spacer(1, 20)]))
            else:
                complete_story.append(trends_header)
                complete_story.append(Spacer(1, 20))
            if not county_trends.empty:
                self.add_toc_entry(f"Detailed Branch Trends Data - {county}", 2, f"trends_table_{county}")
                complete_story.append(Paragraph(f'<a name="trends_table_{county}"></a>Detailed Branch Trends Data:', self.subsection_style))
                trend_data = []
                trend_data.append(['Year', 'Total', 'YoY Chg', 'YoY %', 'Cumul %', 'LMI %', 'MMCT %', 'Both %'])
                for _, row in county_trends.iterrows():
                    trend_data.append([
                        self.format_year(row['year']),
                        self.format_number(row['total_branches']),
                        f"{'+' if row['total_yoy_change_abs'] > 0 else ''}{self.format_number(row['total_yoy_change_abs'])}" if not pd.isna(row['total_yoy_change_abs']) else "N/A",
                        f"{'+' if row['total_yoy_change'] > 0 else ''}{self.format_percentage_table(row['total_yoy_change'])}" if not pd.isna(row['total_yoy_change']) else "N/A",
                        f"{'+' if row['total_cumulative_change'] > 0 else ''}{self.format_percentage_table(row['total_cumulative_change'])}" if not pd.isna(row['total_cumulative_change']) else "N/A",
                        self.format_percentage_table(row['lmict_pct']),
                        self.format_percentage_table(row['mmct_pct']),
                        self.format_percentage_table(row['both_pct'])
                    ])
                trend_table = Table(trend_data, colWidths=[0.8*inch, 1.1*inch, 1*inch, 0.9*inch, 1*inch, 0.9*inch, 0.9*inch, 0.9*inch])
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
            
            # Market Concentration Section
            complete_story.append(PageBreak())
            self.current_page += 1
            if county == 'combined':
                area_name = ' and '.join(self.counties)
                self.add_toc_entry(f"Market Concentration: Largest Banks Analysis - {area_name}", 1, f"market_concentration_{county}")
                complete_story.append(Paragraph(f'<a name="market_concentration_{county}"></a>Market Concentration: Largest Banks Analysis', self.section_style))
            else:
                self.add_toc_entry(f"Market Concentration: Largest Banks Analysis - {county}", 1, f"market_concentration_{county}")
                market_header = Paragraph(f'<a name="market_concentration_{county}"></a>Market Concentration: Largest Banks Analysis', self.section_style)
                complete_story.append(market_header)
            
            if county in top_banks and not county_market_shares.empty:
                    top_bank_data = county_market_shares[county_market_shares['bank_name'].isin(top_banks[county])]
                    if not top_bank_data.empty:
                        if ai_analysis['bank_strategies']:
                            complete_story.extend(self.format_ai_content(ai_analysis['bank_strategies']))
                            complete_story.append(Spacer(1, 15))
                        total_top_branches = top_bank_data['total_branches'].sum()
                        total_county_branches = county_market_shares['total_branches'].sum()
                        top_percentage = (total_top_branches / total_county_branches * 100) if total_county_branches > 0 else 0
                        
                        # Create a more professional summary section
                        complete_story.append(Spacer(1, 10))
                        self.add_toc_entry(f"Market Concentration Summary - {county}", 2, f"market_summary_{county}")
                        complete_story.append(Paragraph(f'<a name="market_summary_{county}"></a>Market Concentration Summary', self.subsection_style))
                        complete_story.append(Spacer(1, 5))
                        if county == 'combined':
                            area_name = ' and '.join(self.counties)
                            complete_story.append(Paragraph(
                                f"As of {max(self.years)}, {len(top_bank_data)} banks control "
                                f"{self.format_percentage(top_percentage)} of all branches in {area_name}, operating "
                                f"{self.format_number(total_top_branches)} out of {self.format_number(total_county_branches)} total branches. "
                                f"This represents a {len(top_bank_data)}-bank oligopoly in the area's banking sector.",
                                self.summary_box_style
                            ))
                        else:
                            complete_story.append(Paragraph(
                                f"As of {max(self.years)}, {len(top_bank_data)} banks control "
                                f"{self.format_percentage(top_percentage)} of all branches in {county}, operating "
                                f"{self.format_number(total_top_branches)} out of {self.format_number(total_county_branches)} total branches. "
                                f"This represents a {len(top_bank_data)}-bank oligopoly in the county's banking sector.",
                                self.summary_box_style
                            ))
                        complete_story.append(Spacer(1, 15))
                        self.add_toc_entry(f"Top Banks Market Share Data - {county}", 2, f"market_share_table_{county}")
                        complete_story.append(Paragraph(f'<a name="market_share_table_{county}"></a>Top Banks Market Share Data:', self.subsection_style))
                        bank_table_data = []
                        bank_table_data.append(['Bank', 'Branches', 'Mkt Share %', 'LMI %', 'MMCT %', 'Both %'])
                        for _, row in top_bank_data.iterrows():
                            bank_table_data.append([
                                Paragraph(self.to_proper_case(row['bank_name']), ParagraphStyle(
                                    'BankName',
                                    parent=self.body_style,
                                    alignment=TA_CENTER,
                                    fontSize=9,
                                    leading=11,
                                    wordWrap='LTR'
                                )),
                                self.format_number(row['total_branches']),
                                self.format_percentage_table(row['market_share']),
                                self.format_percentage_table(row['lmict_pct']),
                                self.format_percentage_table(row['mmct_pct']),
                                self.format_percentage_table(row['both_pct'])
                            ])
                        bank_table = Table(bank_table_data, colWidths=[2.5*inch, 1.1*inch, 1.1*inch, 0.9*inch, 0.9*inch, 1*inch])
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
                        complete_story.append(KeepTogether([bank_table, Spacer(1, 15)]))
                        if not county_bank_analysis.empty:
                            self.add_toc_entry(f"Growth Analysis - {county}", 2, f"growth_analysis_{county}")
                            complete_story.append(Paragraph(f'<a name="growth_analysis_{county}"></a><b>Growth Analysis:</b> The following table shows how the branch counts for these top banks '
                                f"have evolved from {self.years[0]} to {self.years[-1]}, including absolute and percentage changes:", self.body_style))
                            growth_data = []
                            growth_data.append(['Bank', f'Branches\n({self.years[0]})', f'Branches\n({self.years[-1]})', f'Absolute\nChange', f'Percentage\nChange %'])
                            for _, row in county_bank_analysis.iterrows():
                                growth_data.append([
                                    Paragraph(self.to_proper_case(row['bank_name']), ParagraphStyle(
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
                            complete_story.append(KeepTogether([growth_table, Spacer(1, 15)]))
                        if county in bank_analysis and not bank_analysis[county].empty:
                            if ai_analysis['community_impact']:
                                complete_story.extend(self.format_ai_content(ai_analysis['community_impact']))
                                complete_story.append(Spacer(1, 15))
                            self.add_toc_entry(f"Community Impact Comparison Data - {county}", 2, f"community_impact_table_{county}")
                            complete_story.append(Paragraph(f'<a name="community_impact_table_{county}"></a>Community Impact Comparison Data:', self.subsection_style))
                            comparison_data = []
                            comparison_data.append(['Bank', 'LMI %', 'MMCT %', 'Both %', 'LMI vs\nAvg', 'MMCT vs\nAvg'])
                            for _, row in bank_analysis[county].iterrows():
                                bank_current = county_market_shares[county_market_shares['bank_name'] == row['bank_name']]
                                if not bank_current.empty:
                                    bank_lmi = bank_current.iloc[0]['lmict_pct']
                                    bank_mmct = bank_current.iloc[0]['mmct_pct']
                                    bank_both = min(bank_lmi, bank_mmct) if bank_lmi > 0 and bank_mmct > 0 else 0
                                    lmi_vs_avg = f"<font color='green'>▲</font>" if bank_lmi > county_comparisons['county_avg_lmict'] else f"<font color='red'>▼</font>" if bank_lmi < county_comparisons['county_avg_lmict'] else "●"
                                    mmct_vs_avg = f"<font color='green'>▲</font>" if bank_mmct > county_comparisons['county_avg_mmct'] else f"<font color='red'>▼</font>" if bank_mmct < county_comparisons['county_avg_mmct'] else "●"
                                    comparison_data.append([
                                        Paragraph(self.to_proper_case(row['bank_name']), ParagraphStyle(
                                            'BankName',
                                            parent=self.body_style,
                                            alignment=TA_CENTER,
                                            fontSize=9,
                                            leading=11,
                                            wordWrap='LTR'
                                        )),
                                        self.format_percentage_table(bank_lmi),
                                        self.format_percentage_table(bank_mmct),
                                        self.format_percentage_table(bank_both),
                                        lmi_vs_avg,
                                        mmct_vs_avg
                                    ])
                            comparison_table = Table(comparison_data, colWidths=[2.5*inch, 0.9*inch, 0.9*inch, 0.9*inch, 1.1*inch, 1.2*inch])
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
                            complete_story.append(KeepTogether([comparison_table, Spacer(1, 15)]))
            

        
        # Methodology and Technical Notes Section
        complete_story.append(PageBreak())
        self.current_page += 1
        self.add_toc_entry("Methodology and Technical Notes", 1, "methodology")
        complete_story.append(Paragraph('<a name="methodology"></a>Methodology and Technical Notes', self.section_style))
        complete_story.append(Paragraph(
            f"<b>Analysis Period:</b> {years_str}<br/>"
            f"<b>Geographic Scope:</b> {counties_str}<br/>"
            f"<b>Report Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>"
            f"<b>Data Source:</b> FDIC Summary of Deposits<br/>"
            f"<b>Analysis Method:</b> AI-Powered Statistical Analysis with {self.ai_analyzer.provider.upper()}<br/>"
            f"<b>Report Type:</b> Comprehensive Market Analysis",
            self.body_style
        ))
        complete_story.append(Spacer(1, 15))
        complete_story.append(Paragraph(
            f"This analysis examines bank branch trends using FDIC Summary of Deposits data. "
            f"The analysis focuses on three key metrics: total branch counts, the percentage of branches in Low-to-Moderate Income (LMI) tracts, "
            f"and the percentage of branches in Majority-Minority Census Tracts (MMCT). We identify the largest banks by market share "
            f"and analyze their growth patterns and community impact compared to county averages. All analysis is enhanced with "
            f"AI-powered insights using {self.ai_analyzer.provider.upper()} for deeper interpretation of trends and strategic implications.",
            self.body_style
        ))
        complete_story.append(Spacer(1, 15))
        complete_story.append(Paragraph(
            "<b>Data Definitions:</b><br/>"
            "• <b>LMICT:</b> Low-to-Moderate Income Census Tracts - areas with median family income below 80% of the area median income<br/>"
            "• <b>MMCT:</b> Majority-Minority Census Tracts - areas where minority populations represent more than 50% of the total population<br/>"
            "• <b>LMI/MMCT:</b> Branches that serve both low-to-moderate income and majority-minority communities<br/>"
            "• <b>Market Share:</b> Percentage of total branches in the county controlled by each bank",
            self.body_style
        ))
        
        # Now insert the TOC page after the cover page
        toc_story = self.create_toc_page()
        
        # Build the final story with TOC inserted at the right place
        final_story = []
        
        # Find the cover page elements (first few items)
        cover_page_end = 0
        for i, item in enumerate(complete_story):
            if isinstance(item, PageBreak):
                cover_page_end = i + 1
                break
        
        # Add cover page
        final_story.extend(complete_story[:cover_page_end])
        
        # Add TOC page after cover page
        final_story.extend(toc_story)
        final_story.append(PageBreak())
        
        # Add all remaining content
        final_story.extend(complete_story[cover_page_end:])
        
        doc.build(final_story)
        print(f"✅ AI-powered PDF report generated successfully: {output_path}")
        print(f"   - AI provided narrative text only")
        print(f"   - Python handled all tables, charts, and formatting")
        print(f"   - Dynamic table of contents with {len(self.toc_entries)} entries")


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