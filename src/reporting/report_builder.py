"""
Report builder module for creating Excel reports from BigQuery data.
Handles data processing, trend analysis, and Excel export.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
from datetime import datetime
import os


def build_report(raw_data: List[Dict[str, Any]], counties: List[str], years: List[int]) -> Dict[str, pd.DataFrame]:
    """
    Process raw BigQuery data and build comprehensive report dataframes.
    
    Args:
        raw_data: List of dictionaries from BigQuery results
        counties: List of counties in the report
        years: List of years in the report
        
    Returns:
        Dictionary containing multiple dataframes for different report sections
    """
    if not raw_data:
        raise ValueError("No data provided for report building")
    
    # Convert to DataFrame
    df = pd.DataFrame(raw_data)
    
    # Ensure required columns exist
    required_columns = ['bank_name', 'year', 'geoid5', 'county_state', 'total_branches', 'lmict', 'mmct']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    # Clean and prepare data
    df = clean_data(df)
    
    # Build different report sections
    report_data = {
        'summary': create_summary_table(df, counties, years),
        'by_bank': create_bank_summary(df),
        'by_county': create_county_summary(df),
        'trends': create_trend_analysis(df, years),
        'raw_data': df
    }
    
    return report_data


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and prepare the raw data."""
    # Convert numeric columns
    numeric_columns = ['total_branches', 'lmict', 'mmct']
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Convert year to integer
    df['year'] = pd.to_numeric(df['year'], errors='coerce').fillna(0).astype(int)
    
    # Clean bank names
    df['bank_name'] = df['bank_name'].str.strip()
    
    # Remove rows with invalid data
    df = df[df['year'] > 0]
    df = df[df['total_branches'] >= 0]
    
    return df


def create_summary_table(df: pd.DataFrame, counties: List[str], years: List[int]) -> pd.DataFrame:
    """Create a high-level summary table."""
    summary = df.groupby(['county_state', 'year']).agg({
        'total_branches': 'sum',
        'lmict': 'sum',
        'mmct': 'sum',
        'bank_name': 'nunique'
    }).reset_index()
    
    summary.columns = ['County', 'Year', 'Total Branches', 'LMI Branches', 'Minority Branches', 'Number of Banks']
    
    # Calculate percentages
    summary['LMI %'] = (summary['LMI Branches'] / summary['Total Branches'] * 100).round(1)
    summary['Minority %'] = (summary['Minority Branches'] / summary['Total Branches'] * 100).round(1)
    
    return summary


def create_bank_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Create summary by bank."""
    bank_summary = df.groupby(['bank_name', 'county_state', 'year']).agg({
        'total_branches': 'sum',
        'lmict': 'sum',
        'mmct': 'sum'
    }).reset_index()
    
    # Calculate percentages
    bank_summary['LMI %'] = (bank_summary['lmict'] / bank_summary['total_branches'] * 100).round(1)
    bank_summary['Minority %'] = (bank_summary['mmct'] / bank_summary['total_branches'] * 100).round(1)
    
    # Rename columns
    bank_summary.columns = ['Bank Name', 'County', 'Year', 'Total Branches', 'LMI Branches', 'Minority Branches', 'LMI %', 'Minority %']
    
    return bank_summary.sort_values(['Bank Name', 'County', 'Year'])


def create_county_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Create summary by county."""
    county_summary = df.groupby(['county_state', 'year']).agg({
        'total_branches': 'sum',
        'lmict': 'sum',
        'mmct': 'sum',
        'bank_name': 'nunique'
    }).reset_index()
    
    # Calculate percentages
    county_summary['LMI %'] = (county_summary['lmict'] / county_summary['total_branches'] * 100).round(1)
    county_summary['Minority %'] = (county_summary['mmct'] / county_summary['total_branches'] * 100).round(1)
    
    # Rename columns
    county_summary.columns = ['County', 'Year', 'Total Branches', 'LMI Branches', 'Minority Branches', 'Number of Banks', 'LMI %', 'Minority %']
    
    return county_summary.sort_values(['County', 'Year'])


def create_trend_analysis(df: pd.DataFrame, years: List[int]) -> pd.DataFrame:
    """Create trend analysis across years."""
    if len(years) < 2:
        # Not enough years for trend analysis
        return pd.DataFrame()
    
    # Aggregate by year
    yearly_totals = df.groupby('year').agg({
        'total_branches': 'sum',
        'lmict': 'sum',
        'mmct': 'sum',
        'bank_name': 'nunique'
    }).reset_index()
    
    # Calculate year-over-year changes
    yearly_totals['Total Branches YoY %'] = yearly_totals['total_branches'].pct_change() * 100
    yearly_totals['LMI Branches YoY %'] = yearly_totals['lmict'].pct_change() * 100
    yearly_totals['Minority Branches YoY %'] = yearly_totals['mmct'].pct_change() * 100
    
    # Calculate percentages
    yearly_totals['LMI %'] = (yearly_totals['lmict'] / yearly_totals['total_branches'] * 100).round(1)
    yearly_totals['Minority %'] = (yearly_totals['mmct'] / yearly_totals['total_branches'] * 100).round(1)
    
    # Rename columns
    yearly_totals.columns = ['Year', 'Total Branches', 'LMI Branches', 'Minority Branches', 'Number of Banks', 
                           'Total Branches YoY %', 'LMI Branches YoY %', 'Minority Branches YoY %', 'LMI %', 'Minority %']
    
    return yearly_totals.round(1)


def save_excel_report(report_data: Dict[str, pd.DataFrame], output_path: str):
    """
    Save the report data to an Excel file with multiple sheets.
    
    Args:
        report_data: Dictionary containing dataframes for different report sections
        output_path: Path where the Excel file should be saved
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Create Excel writer
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        
        # Write each dataframe to a separate sheet
        if 'summary' in report_data and not report_data['summary'].empty:
            report_data['summary'].to_excel(writer, sheet_name='Summary', index=False)
        
        if 'by_bank' in report_data and not report_data['by_bank'].empty:
            report_data['by_bank'].to_excel(writer, sheet_name='By Bank', index=False)
        
        if 'by_county' in report_data and not report_data['by_county'].empty:
            report_data['by_county'].to_excel(writer, sheet_name='By County', index=False)
        
        if 'trends' in report_data and not report_data['trends'].empty:
            report_data['trends'].to_excel(writer, sheet_name='Trends', index=False)
        
        if 'raw_data' in report_data and not report_data['raw_data'].empty:
            report_data['raw_data'].to_excel(writer, sheet_name='Raw Data', index=False)
        
        # Auto-adjust column widths
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width


def generate_report_metadata(counties: List[str], years: List[int], record_count: int) -> Dict[str, Any]:
    """Generate metadata for the report."""
    return {
        'generated_at': datetime.now().isoformat(),
        'counties': counties,
        'years': years,
        'total_records': record_count,
        'report_type': 'FDIC Bank Branch Analysis'
    }
