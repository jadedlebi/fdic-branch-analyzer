# FDIC Analyzer Logging System

The FDIC Analyzer now includes a comprehensive logging system that tracks all runs of the tool, including costs, queries, user information, and performance metrics.

## Overview

The logging system automatically tracks:

- **Cost estimates** for AI API calls and BigQuery queries
- **Query details** (counties, years, SQL executed)
- **End user information** (IP, user agent, session data)
- **Performance metrics** (execution time, data volume)
- **Error tracking** and success rates
- **Generated files** (Excel and PDF reports)

## Files Generated

The logging system creates several files in the `data/logs/` directory:

- `runs.csv` - Summary of all runs in CSV format
- `detailed/` - Directory containing detailed JSON logs for each run
- `detailed/{run_id}.json` - Detailed information for each individual run

## Cost Tracking

### AI Costs
The system tracks costs for both Claude and OpenAI APIs:

- **Claude 3.5 Sonnet**: $0.003 per 1K input tokens, $0.015 per 1K output tokens
- **Claude 3 Opus**: $0.015 per 1K input tokens, $0.075 per 1K output tokens
- **GPT-4**: $0.03 per 1K input tokens, $0.06 per 1K output tokens
- **GPT-4 Turbo**: $0.01 per 1K input tokens, $0.03 per 1K output tokens

### BigQuery Costs
- **Standard rate**: $5.00 per TB processed
- **Query statistics**: Bytes processed, number of queries

## User Information Tracking

For web interface runs, the system captures:

- **IP Address**: User's IP address (with proxy detection)
- **User Agent**: Browser and operating system information
- **Session ID**: Unique session identifier
- **Interface Type**: "web" or "cli"

## Usage

### Viewing Logs

Use the `view_logs.py` script to examine the logs:

```bash
# Show summary of all runs
python scripts/view_logs.py --summary

# List recent runs
python scripts/view_logs.py --list

# Show detailed information for a specific run
python scripts/view_logs.py --detailed <run_id>

# Generate Excel report of all runs
python scripts/view_logs.py --generate-report --output runs_report.xlsx
```

### Generating Reports

Use the `generate_run_report.py` script to create comprehensive reports:

```bash
# Generate detailed Excel report
python scripts/generate_run_report.py --detailed --output fdic_runs_report.xlsx

# Generate summary CSV
python scripts/generate_run_report.py --summary --output fdic_runs_summary.csv

# Generate both (default)
python scripts/generate_run_report.py --output fdic_runs_report.xlsx
```

## Report Contents

### Excel Report Sheets

1. **All Runs**: Complete data for all runs
2. **Cost Analysis**: Summary of costs and usage
3. **User Analysis**: Browser and interface usage statistics
4. **Performance Analysis**: Execution times and performance metrics
5. **Top Counties**: Most frequently analyzed counties
6. **Year Usage**: Analysis by year
7. **Errors**: Failed runs and error messages

### CSV Summary

The CSV summary includes key columns:
- Run ID, timestamp, interface type
- Counties and years analyzed
- Execution time and records processed
- AI and BigQuery usage statistics
- Cost estimates
- Success/failure status

## Data Privacy

The logging system respects user privacy:

- **IP addresses** are logged but not shared in reports
- **User agent strings** are parsed for browser/OS info only
- **Session IDs** are anonymized
- **No personal data** is collected beyond technical usage statistics

## Configuration

### Log Directory
Logs are stored in `data/logs/` by default. You can change this by modifying the `DATA_DIR` in `config/config.py`.

### Cost Estimates
Cost estimates are based on current API pricing. Update the `COST_ESTIMATES` dictionary in `src/utils/run_logger.py` if pricing changes.

### BigQuery Cost Rate
The BigQuery cost rate is set to $5.00 per TB in `src/utils/run_logger.py`. Update `BQ_COST_PER_TB` if your pricing differs.

## Integration

The logging system is automatically integrated into:

- **Web interface** (`app.py`): Tracks all web-based runs
- **Command-line interface** (`main.py`): Tracks all CLI runs
- **AI analysis**: Tracks token usage and costs
- **BigQuery queries**: Tracks query statistics and costs

## Monitoring

### Real-time Monitoring
You can monitor usage in real-time by checking the logs:

```bash
# Watch for new runs
tail -f data/logs/runs.csv

# Check recent detailed logs
ls -la data/logs/detailed/ | tail -10
```

### Cost Alerts
Set up monitoring for cost thresholds:

```bash
# Check if total cost exceeds threshold
python -c "
import pandas as pd
df = pd.read_csv('data/logs/runs.csv')
total_cost = df['total_cost_estimate'].sum()
if total_cost > 100:  # $100 threshold
    print(f'Warning: Total cost is ${total_cost:.2f}')
"
```

## Troubleshooting

### Common Issues

1. **No logs generated**: Check that the `data/logs/` directory exists and is writable
2. **Missing cost estimates**: Verify API keys are set and AI calls are working
3. **Incorrect BigQuery costs**: Check that BigQuery client is properly configured

### Debug Mode
Enable debug logging by adding to your environment:

```bash
export FDIC_DEBUG=1
```

This will provide additional logging information during runs.

## API Reference

### RunLogger Class

```python
from src.utils.run_logger import run_logger

# Start a new run
run_id = run_logger.start_run(
    counties=['Cook County, Illinois'],
    years=[2020, 2021],
    interface_type='web',
    user_ip='192.168.1.1',
    user_agent='Mozilla/5.0...'
)

# Update run metadata
run_logger.update_run(run_id, ai_calls=5, records_processed=1000)

# End the run
run_logger.end_run(run_id, success=True)

# Get summary
df = run_logger.get_runs_summary()
cost_summary = run_logger.get_cost_summary()
```

### Tracked Components

```python
# Tracked BigQuery client
from src.utils.bq_tracker import TrackedBigQueryClient
bq_client = TrackedBigQueryClient(run_id)
results = bq_client.execute_query(sql, county, year)

# Tracked AI analyzer
from src.analysis.ai_tracker import TrackedAIAnalyzer
ai_analyzer = TrackedAIAnalyzer(run_id)
summary = ai_analyzer.generate_executive_summary(data)
```

## Future Enhancements

Planned improvements to the logging system:

1. **Real-time dashboard**: Web interface for monitoring usage
2. **Email alerts**: Notifications for cost thresholds or errors
3. **Advanced analytics**: Usage patterns and optimization suggestions
4. **Export formats**: Additional report formats (PDF, JSON)
5. **API endpoints**: REST API for accessing log data
6. **Data retention**: Automatic cleanup of old logs
7. **Cost optimization**: Suggestions for reducing costs 