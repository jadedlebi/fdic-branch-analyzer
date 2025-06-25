# AI-Assisted FDIC Bank Branch Report Generator

An intelligent system that generates comprehensive reports on FDIC bank branch data using natural language prompts, GPT-4, and BigQuery.

## Overview

This system allows you to generate detailed Excel reports on FDIC bank branch data by simply describing what you want in natural language. The AI extracts the relevant parameters (counties and years) and automatically queries BigQuery to generate comprehensive reports.

## Features

- **Natural Language Interface**: Describe your report requirements in plain English
- **AI-Powered Parameter Extraction**: GPT-4 automatically extracts counties and years from your prompt
- **Comprehensive Data Analysis**: Includes total branches, LMI branches, and minority census tract branches
- **Multi-Sheet Excel Reports**: Organized data across multiple sheets (Summary, By Bank, By County, Trends, Raw Data)
- **Trend Analysis**: Year-over-year comparisons and percentage calculations
- **Flexible Querying**: Support for multiple counties and years in a single report

## Project Structure

```
branch_ai/
├── main.py                     # Main orchestration script
├── config.py                   # Configuration constants
├── gpt_utils.py                # GPT API integration and parameter extraction
├── bq_utils.py                 # BigQuery connection and query execution
├── report_builder.py           # Data processing and Excel report generation
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── prompts/
│   └── reporting_prompt.txt    # Natural language prompt template
│
├── query_templates/
│   └── branch_report.sql       # BigQuery SQL query template
│
├── data/
│   └── output/                 # Generated Excel reports
│
├── id/
│   └── hdma1-242116-11deed6edade.json   # Google service account credentials
│
└── .env                        # Environment variables (create this)
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Credentials

#### OpenAI API Key
Create a `.env` file in the project root:
```
OPENAI_API_KEY=your_openai_api_key_here
```

#### BigQuery Credentials
Ensure your Google service account JSON file is in the `id/` directory and properly referenced in `config.py`.

### 3. Verify Configuration

Check that the following paths are correct in `config.py`:
- `BQ_CREDENTIALS_PATH`: Path to your Google service account JSON file
- `PROJECT_ID`: Your BigQuery project ID
- `PROMPT_PATH`: Path to the prompt template file
- `SQL_TEMPLATE_PATH`: Path to the SQL query template

## Usage

### 1. Create Your Prompt

Edit `prompts/reporting_prompt.txt` with your natural language request. Example:

```
Generate a comprehensive FDIC bank branch analysis report for Los Angeles County, California and Cook County, Illinois for the years 2020, 2021, and 2022. The report should include data on total branches, LMI (Low-to-Moderate Income) branches, and minority census tract branches for each bank operating in these counties during the specified time period.
```

### 2. Run the Report Generator

```bash
python main.py
```

### 3. Find Your Report

The generated Excel file will be saved in `data/output/` with a timestamp and descriptive filename.

## Report Contents

The generated Excel file contains multiple sheets:

1. **Summary**: High-level overview by county and year
2. **By Bank**: Detailed breakdown by individual banks
3. **By County**: County-level aggregations
4. **Trends**: Year-over-year analysis and percentage changes
5. **Raw Data**: Complete dataset from BigQuery

## Data Fields

- **Total Branches**: Number of bank branches in the area
- **LMI Branches**: Branches in Low-to-Moderate Income census tracts
- **Minority Branches**: Branches in minority census tracts
- **LMI %**: Percentage of branches in LMI areas
- **Minority %**: Percentage of branches in minority areas

## Customization

### Adding New Counties
Simply include the county name in your prompt in "County, State" format (e.g., "Los Angeles, CA").

### Modifying Years
Include specific years in your prompt, or the system will use recent years by default.

### Custom SQL Queries
Modify `query_templates/branch_report.sql` to include additional data fields or filtering criteria.

## Error Handling

The system includes comprehensive error handling for:
- Missing credentials
- Invalid BigQuery queries
- GPT API failures
- Data processing errors
- File I/O issues

## Troubleshooting

### Common Issues

1. **"Credentials file not found"**: Check that your Google service account JSON file is in the correct location
2. **"OpenAI API key not found"**: Ensure your `.env` file contains the correct API key
3. **"No data found"**: Verify that the specified counties and years exist in your BigQuery dataset
4. **"BigQuery connection failed"**: Check your project ID and credentials

### Testing Connections

You can test individual components:

```python
# Test BigQuery connection
from bq_utils import test_connection
print(test_connection())

# Test GPT API
from gpt_utils import ask_gpt
response = ask_gpt("Hello, world!")
print(response)
```

## Data Sources

The system queries the following BigQuery tables:
- `branches.sod`: Current Summary of Deposits data
- `branches.sod_legacy`: Historical Summary of Deposits data
- `geo.cbsa_to_county`: Geographic mapping data

## License

This project is for internal use. Please ensure compliance with all applicable data usage agreements and API terms of service.

## Support

For issues or questions, check the error messages in the console output and refer to the troubleshooting section above. 