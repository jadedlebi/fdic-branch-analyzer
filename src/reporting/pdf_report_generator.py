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
from analysis.gpt_utils import AIAnalyzer


class EnhancedPDFReportGenerator:
    def __init__(self, data: pd.DataFrame, counties: List[str], years: List[int]):
        """
        Initialize the enhanced PDF report generator.
        
        Args:
            data: DataFrame with branch data
            counties: List of counties analyzed
            years: List of years analyzed
        """
        self.data = data.copy()
        self.counties = counties
        self.years = sorted(years)
        self.styles = getSampleStyleSheet()
        self.setup_enhanced_styles()
        self.ai_analyzer = AIAnalyzer()
        
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
            fontName='Helvetica',
            textColor=colors.HexColor('#2d3748')
        )
        
        # Enhanced table header style
        self.table_header_style = ParagraphStyle(
            'EnhancedTableHeader',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=5,
            leading=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            textColor=colors.white
        )
        
        # Enhanced table cell style
        self.table_cell_style = ParagraphStyle(
            'EnhancedTableCell',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=3,
            leading=11,
            alignment=TA_CENTER,
            fontName='Helvetica',
            textColor=colors.HexColor('#2d3748')
        )
        
        # Key findings style
        self.key_findings_style = ParagraphStyle(
            'KeyFindings',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=8,
            leading=16,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#2d3748'),
            leftIndent=20
        )
        
        # Bullet point style
        self.bullet_style = ParagraphStyle(
            'BulletPoint',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            leading=14,
            alignment=TA_LEFT,
            fontName='Helvetica',
            textColor=colors.HexColor('#2d3748'),
            leftIndent=25,
            firstLineIndent=-15
        )
        
        # Numbered list style
        self.numbered_style = ParagraphStyle(
            'NumberedList',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            leading=14,
            alignment=TA_LEFT,
            fontName='Helvetica',
            textColor=colors.HexColor('#2d3748'),
            leftIndent=25,
            firstLineIndent=-15
        )
        
        # Bold keyword style
        self.bold_style = ParagraphStyle(
            'BoldKeyword',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=10,
            leading=15,
            alignment=TA_JUSTIFY,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#2d3748')
        )
        
        # Page number style
        self.page_number_style = ParagraphStyle(
            'PageNumber',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=0,
            leading=12,
            alignment=TA_CENTER,
            fontName='Helvetica',
            textColor=colors.HexColor('#4a5568')
        )
        
        # Summary box style for highlighted information
        self.summary_box_style = ParagraphStyle(
            'SummaryBox',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            spaceBefore=8,
            leading=15,
            alignment=TA_JUSTIFY,
            fontName='Helvetica',
            textColor=colors.HexColor('#2d3748'),
            leftIndent=10,
            rightIndent=10,
            backColor=colors.HexColor('#f7fafc'),
            borderWidth=1,
            borderColor=colors.HexColor('#e2e8f0'),
            borderPadding=8
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
            
            # Calculate percentages
            yearly_stats['lmict_pct'] = (yearly_stats['lmict'] / yearly_stats['total_branches'] * 100).round(2)
            yearly_stats['mmct_pct'] = (yearly_stats['mmct'] / yearly_stats['total_branches'] * 100).round(2)
            # Calculate "Both %" as the minimum of LMI % and MMCT % (theoretical maximum overlap)
            # Since we don't have actual intersection data, this represents the maximum possible overlap
            yearly_stats['both_pct'] = np.minimum(yearly_stats['lmict_pct'], yearly_stats['mmct_pct']).round(2)
            
            # Calculate year-over-year changes
            yearly_stats['total_yoy_change'] = yearly_stats['total_branches'].pct_change() * 100
            yearly_stats['total_yoy_change_abs'] = yearly_stats['total_branches'].diff()
            yearly_stats['lmict_yoy_change'] = yearly_stats['lmict_pct'].pct_change() * 100
            yearly_stats['mmct_yoy_change'] = yearly_stats['mmct_pct'].pct_change() * 100
            
            # Calculate cumulative changes from first year
            first_year = yearly_stats['total_branches'].iloc[0]
            yearly_stats['total_cumulative_change'] = ((yearly_stats['total_branches'] - first_year) / first_year * 100).round(2)
            
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
            
            bank_stats['market_share'] = (bank_stats['total_branches'] / total_county_branches * 100).round(2)
            bank_stats['lmict_pct'] = (bank_stats['lmict'] / bank_stats['total_branches'] * 100).round(2)
            bank_stats['mmct_pct'] = (bank_stats['mmct'] / bank_stats['total_branches'] * 100).round(2)
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
                
                # Get current year demographics
                current_lmi_pct = last_year_data['lmict_pct'].iloc[0] if not last_year_data.empty else 0
                current_mmct_pct = last_year_data['mmct_pct'].iloc[0] if not last_year_data.empty else 0
                
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
            'trends': trends.to_dict('records') if hasattr(trends, 'empty') and not trends.empty else [],
            'market_shares': market_shares.to_dict('records') if hasattr(market_shares, 'empty') and not market_shares.empty else [],
            'bank_analysis': bank_analysis.to_dict('records') if hasattr(bank_analysis, 'empty') and not bank_analysis.empty else [],
            'comparisons': comparisons
        }
        # Prompts are now explicit: only narrative, no tables or formatting
        executive_summary = self.ai_analyzer.generate_executive_summary(analysis_data)
        overall_trends_analysis = self.ai_analyzer.analyze_overall_trends(analysis_data)
        bank_strategy_analysis = self.ai_analyzer.analyze_bank_strategies(analysis_data)
        community_impact_analysis = self.ai_analyzer.analyze_community_impact(analysis_data)
        key_findings = self.ai_analyzer.generate_key_findings(analysis_data)
        conclusion_analysis = self.ai_analyzer.generate_conclusion(analysis_data)
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
                        # Format numbered items
                        formatted_line = f"• {line}"
                        formatted_content.append(Paragraph(formatted_line, self.numbered_style))
                formatted_content.append(Spacer(1, 8))
                
            # Check if this is a bullet point list
            elif section.startswith('•') or section.startswith('-') or section.startswith('*'):
                # Handle bullet point lists
                lines = section.split('\n')
                for line in lines:
                    line = line.strip()
                    if line:
                        # Clean up bullet point markers
                        line = re.sub(r'^[•\-*]\s*', '', line)
                        formatted_line = f"• {line}"
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
                    formatted_content.append(Paragraph(section, self.body_style))
                else:
                    # Handle inline bold text properly
                    # Replace **text** with <b>text</b> for inline bold
                    formatted_section = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', section)
                    # Replace *text* with <b>text</b> for single asterisk bold (if not already handled)
                    formatted_section = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<b>\1</b>', formatted_section)
                    formatted_content.append(Paragraph(formatted_section, self.body_style))
                formatted_content.append(Spacer(1, 8))
                
            else:
                # Regular paragraph
                formatted_content.append(Paragraph(section, self.body_style))
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
                # Format numbered items
                formatted_content.append(Paragraph(line, self.numbered_style))
            elif line.startswith('•') or line.startswith('-') or line.startswith('*'):
                # Format bullet points
                line = re.sub(r'^[•\-*]\s*', '', line)
                formatted_line = f"• {line}"
                formatted_content.append(Paragraph(formatted_line, self.bullet_style))
            else:
                # Regular text
                formatted_content.append(Paragraph(line, self.body_style))
        
        return formatted_content
    
    def generate_enhanced_pdf_report(self, output_path: str):
        """Generate the complete enhanced PDF report with comprehensive analysis. AI only provides narrative text; all tables and formatting are handled by Python."""
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
        story = []
        
        # Enhanced Cover Page
        counties_str = " and ".join(self.counties)
        years_str = f"{self.years[0]}–{self.years[-1]}"
        logo_path = "./ncrc_logo.jpg"
        if os.path.exists(logo_path):
            from reportlab.platypus import Image
            logo_img = Image(logo_path, width=2.8*inch, height=1*inch)
            story.append(logo_img)
            story.append(Spacer(1, 20))
        else:
            story.append(Paragraph("[NCRC LOGO]", self.subtitle_style))
            story.append(Spacer(1, 20))
        # Title with line breaks
        title_text = f"{counties_str}<br/>Bank Branch Trends<br/>({years_str})"
        story.append(Paragraph(title_text, self.title_style))
        story.append(Spacer(1, 40))
        story.append(Paragraph("AI-Powered Banking Market Intelligence", self.subtitle_style))
        story.append(Spacer(1, 30))
        story.append(Paragraph(f"Report Generated: {datetime.now().strftime('%B %d, %Y')}", self.body_style))
        story.append(PageBreak())
        
        # Calculate all enhanced data
        trends = self.calculate_enhanced_trends()
        market_shares = self.calculate_enhanced_market_share()
        top_banks = self.get_enhanced_top_banks(market_shares)
        bank_analysis = self.analyze_enhanced_bank_growth(top_banks)
        comparisons = self.calculate_enhanced_comparisons(bank_analysis)
        
        # Generate enhanced AI analysis for each county (narrative only)
        for county in self.counties:
            if county in trends and county in market_shares:
                county_trends = trends[county]
                county_market_shares = market_shares[county]
                county_bank_analysis = bank_analysis.get(county, pd.DataFrame())
                county_comparisons = comparisons.get(county, {})
                ai_analysis = self.generate_enhanced_ai_analysis(
                    {'county': county},
                    county_trends,
                    county_market_shares,
                    county_bank_analysis,
                    county_comparisons
                )
                # Executive Summary Section
                story.append(PageBreak())
                story.append(Paragraph("Executive Summary", self.section_style))
                if ai_analysis['executive_summary']:
                    story.extend(self.format_ai_content(ai_analysis['executive_summary']))
                story.append(Spacer(1, 20))
                
                # Key Findings Section
                story.append(PageBreak())
                story.append(Paragraph("Key Findings", self.section_style))
                if ai_analysis['key_findings']:
                    story.extend(self.format_key_findings(ai_analysis['key_findings']))
                story.append(Spacer(1, 20))
                
                # Understanding the Data Section
                story.append(PageBreak())
                story.append(Paragraph("Understanding the Data", self.section_style))
                story.append(Paragraph(
                    f"This analysis examines bank branch trends in {county} from {years_str} using FDIC Summary of Deposits data. "
                    f"We focus on three key metrics:",
                    self.body_style
                ))
                story.append(Paragraph("• <b>LMICT (Low-to-Moderate Income Census Tracts):</b> Branches located in areas with median family income below 80% of the area median income", self.bullet_style))
                story.append(Paragraph("• <b>MMCT (Majority-Minority Census Tracts):</b> Branches located in areas where minority populations represent more than 50% of the total population", self.bullet_style))
                story.append(Paragraph("• <b>LMI/MMCT:</b> Branches that serve both low-to-moderate income and majority-minority communities", self.bullet_style))
                story.append(Paragraph(
                    f"<b>Important Note:</b> MMCT designations increased significantly with the 2020 census and became effective in 2022. "
                    f"This means MMCT percentages may show notable changes between 2021 and 2022, reflecting the updated census data rather than actual branch relocations.",
                    self.body_style
                ))
                story.append(Spacer(1, 20))
                
                # Overall Branch Trends Section
                story.append(PageBreak())
                story.append(Paragraph("Overall Branch Trends", self.section_style))
                if ai_analysis['overall_trends']:
                    story.extend(self.format_ai_content(ai_analysis['overall_trends']))
                    story.append(Spacer(1, 20))
                if not county_trends.empty:
                    story.append(Paragraph("Detailed Branch Trends Data:", self.subsection_style))
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
                    story.append(KeepTogether([trend_table, Spacer(1, 15)]))
                # Market Concentration Section
                story.append(PageBreak())
                story.append(Paragraph("Market Concentration: Largest Banks Analysis", self.section_style))
                if county in top_banks and not county_market_shares.empty:
                    top_bank_data = county_market_shares[county_market_shares['bank_name'].isin(top_banks[county])]
                    if not top_bank_data.empty:
                        if ai_analysis['bank_strategies']:
                            story.extend(self.format_ai_content(ai_analysis['bank_strategies']))
                            story.append(Spacer(1, 15))
                        total_top_branches = top_bank_data['total_branches'].sum()
                        total_county_branches = county_market_shares['total_branches'].sum()
                        top_percentage = (total_top_branches / total_county_branches * 100) if total_county_branches > 0 else 0
                        
                        # Create a more professional summary section
                        story.append(Spacer(1, 10))
                        story.append(Paragraph("Market Concentration Summary", self.subsection_style))
                        story.append(Spacer(1, 5))
                        story.append(Paragraph(
                            f"As of {max(self.years)}, {len(top_bank_data)} banks control "
                            f"{self.format_percentage(top_percentage)} of all branches in {county}, operating "
                            f"{self.format_number(total_top_branches)} out of {self.format_number(total_county_branches)} total branches. "
                            f"This represents a {len(top_bank_data)}-bank oligopoly in the county's banking sector.",
                            self.summary_box_style
                        ))
                        story.append(Spacer(1, 15))
                        story.append(Paragraph("Top Banks Market Share Data:", self.subsection_style))
                        bank_table_data = []
                        bank_table_data.append(['Bank', 'Branches', 'Mkt Share %', 'LMI %', 'MMCT %', 'Both %'])
                        for _, row in top_bank_data.iterrows():
                            bank_table_data.append([
                                Paragraph(row['bank_name'], ParagraphStyle(
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
                        story.append(KeepTogether([bank_table, Spacer(1, 15)]))
                        if not county_bank_analysis.empty:
                            story.append(Paragraph(
                                f"<b>Growth Analysis:</b> The following table shows how the branch counts for these top banks "
                                f"have evolved from {self.years[0]} to {self.years[-1]}, including absolute and percentage changes:",
                                self.body_style
                            ))
                            growth_data = []
                            growth_data.append(['Bank', f'Branches\n({self.years[0]})', f'Branches\n({self.years[-1]})', f'Absolute\nChange', f'Percentage\nChange %'])
                            for _, row in county_bank_analysis.iterrows():
                                growth_data.append([
                                    Paragraph(row['bank_name'], ParagraphStyle(
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
                            story.append(KeepTogether([growth_table, Spacer(1, 15)]))
                        if county in bank_analysis and not bank_analysis[county].empty:
                            if ai_analysis['community_impact']:
                                story.extend(self.format_ai_content(ai_analysis['community_impact']))
                                story.append(Spacer(1, 15))
                            story.append(Paragraph("Community Impact Comparison Data:", self.subsection_style))
                            comparison_data = []
                            comparison_data.append(['Bank', 'LMI %', 'MMCT %', 'Both %', 'LMI vs\nAvg', 'MMCT vs\nAvg'])
                            for _, row in bank_analysis[county].iterrows():
                                bank_current = county_market_shares[county_market_shares['bank_name'] == row['bank_name']]
                                if not bank_current.empty:
                                    bank_lmi = bank_current.iloc[0]['lmict_pct']
                                    bank_mmct = bank_current.iloc[0]['mmct_pct']
                                    bank_both = min(bank_lmi, bank_mmct) if bank_lmi > 0 and bank_mmct > 0 else 0
                                    lmi_vs_avg = "▲" if bank_lmi > county_comparisons['county_avg_lmict'] else "▼" if bank_lmi < county_comparisons['county_avg_lmict'] else "●"
                                    mmct_vs_avg = "▲" if bank_mmct > county_comparisons['county_avg_mmct'] else "▼" if bank_mmct < county_comparisons['county_avg_mmct'] else "●"
                                    comparison_data.append([
                                        Paragraph(row['bank_name'], ParagraphStyle(
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
                            story.append(KeepTogether([comparison_table, Spacer(1, 15)]))
                # Conclusion Section
                story.append(PageBreak())
                story.append(Paragraph("Conclusion and Strategic Implications", self.section_style))
                if ai_analysis['conclusion']:
                    story.extend(self.format_ai_content(ai_analysis['conclusion']))
                else:
                    if not county_trends.empty:
                        first_year_total = county_trends['total_branches'].iloc[0]
                        last_year_total = county_trends['total_branches'].iloc[-1]
                        total_change = last_year_total - first_year_total
                        change_direction = "declined" if total_change < 0 else "increased" if total_change > 0 else "remained stable"
                        story.append(Paragraph(
                            f"In summary, {county} experienced a {change_direction} in bank branches from {self.years[0]} to {self.years[-1]}, "
                            f"changing from {self.format_number(first_year_total)} to {self.format_number(last_year_total)} branches. "
                            f"These trends reflect the evolving landscape of banking in {county}: a more consolidated branch network "
                            f"that is increasingly concentrated among major institutions while maintaining varying levels of commitment "
                            f"to serving diverse and underserved communities.",
                            self.body_style
                        ))
        # Methodology and Technical Notes Section
        story.append(PageBreak())
        story.append(Paragraph("Methodology and Technical Notes", self.section_style))
        story.append(Paragraph(
            f"<b>Analysis Period:</b> {years_str}<br/>"
            f"<b>Geographic Scope:</b> {counties_str}<br/>"
            f"<b>Report Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>"
            f"<b>Data Source:</b> FDIC Summary of Deposits<br/>"
            f"<b>Analysis Method:</b> AI-Powered Statistical Analysis with {self.ai_analyzer.provider.upper()}<br/>"
            f"<b>Report Type:</b> Comprehensive Market Analysis",
            self.body_style
        ))
        story.append(Spacer(1, 15))
        story.append(Paragraph(
            f"This analysis examines bank branch trends using FDIC Summary of Deposits data. "
            f"The analysis focuses on three key metrics: total branch counts, the percentage of branches in Low-to-Moderate Income (LMI) tracts, "
            f"and the percentage of branches in Majority-Minority Census Tracts (MMCT). We identify the largest banks by market share "
            f"and analyze their growth patterns and community impact compared to county averages. All analysis is enhanced with "
            f"AI-powered insights using {self.ai_analyzer.provider.upper()} for deeper interpretation of trends and strategic implications.",
            self.body_style
        ))
        story.append(Spacer(1, 15))
        story.append(Paragraph(
            "<b>Data Definitions:</b><br/>"
            "• <b>LMICT:</b> Low-to-Moderate Income Census Tracts - areas with median family income below 80% of the area median income<br/>"
            "• <b>MMCT:</b> Majority-Minority Census Tracts - areas where minority populations represent more than 50% of the total population<br/>"
            "• <b>LMI/MMCT:</b> Branches that serve both low-to-moderate income and majority-minority communities<br/>"
            "• <b>Market Share:</b> Percentage of total branches in the county controlled by each bank",
            self.body_style
        ))
        doc.build(story)
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