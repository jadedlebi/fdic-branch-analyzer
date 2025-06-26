# FDIC Branch Analyzer API Documentation

## Overview

The FDIC Branch Analyzer provides a RESTful API for generating banking market analysis reports. This API allows external applications to integrate with the analysis engine and generate reports programmatically.

## Base URL

```
https://api.fdic-analyzer.ncrc.org
```

## Authentication

All API requests require authentication using API keys. Include your API key in the request headers:

```
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### 1. Generate Analysis Report

**POST** `/api/v1/analyze`

Generate a comprehensive banking market analysis report.

#### Request Body

```json
{
  "counties": ["Cook County, Illinois", "Los Angeles County, California"],
  "years": [2020, 2021, 2022],
  "format": "both",
  "include_ai_analysis": true
}
```

#### Parameters

- `counties` (array, required): List of counties to analyze
- `years` (array, required): List of years to analyze (2017-2024)
- `format` (string, optional): Output format - "excel", "pdf", or "both" (default: "both")
- `include_ai_analysis` (boolean, optional): Include AI-generated insights (default: true)

#### Response

```json
{
  "success": true,
  "job_id": "job_12345",
  "message": "Analysis started successfully",
  "estimated_completion": "2024-01-15T10:30:00Z"
}
```

### 2. Get Analysis Status

**GET** `/api/v1/status/{job_id}`

Check the status of an analysis job.

#### Response

```json
{
  "success": true,
  "job_id": "job_12345",
  "status": "completed",
  "progress": 100,
  "download_url": "https://api.fdic-analyzer.ncrc.org/download/job_12345",
  "created_at": "2024-01-15T10:00:00Z",
  "completed_at": "2024-01-15T10:25:00Z"
}
```

### 3. Download Report

**GET** `/api/v1/download/{job_id}`

Download the generated report files.

#### Response

Returns a ZIP file containing:
- `fdic_branch_analysis.xlsx` - Excel report
- `fdic_branch_analysis.pdf` - PDF report
- `analysis_metadata.json` - Report metadata

### 4. Get Available Counties

**GET** `/api/v1/counties`

Get a list of all available counties in the database.

#### Response

```json
{
  "success": true,
  "counties": [
    "Cook County, Illinois",
    "Los Angeles County, California",
    "Harris County, Texas"
  ],
  "total_count": 3142
}
```

### 5. Get Available Years

**GET** `/api/v1/years`

Get a list of available years in the database.

#### Response

```json
{
  "success": true,
  "years": [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
  "total_count": 8
}
```

## Error Responses

### 400 Bad Request

```json
{
  "success": false,
  "error": "Invalid parameters",
  "details": {
    "counties": "At least one county is required",
    "years": "Years must be between 2017 and 2024"
  }
}
```

### 401 Unauthorized

```json
{
  "success": false,
  "error": "Invalid API key"
}
```

### 404 Not Found

```json
{
  "success": false,
  "error": "Job not found"
}
```

### 500 Internal Server Error

```json
{
  "success": false,
  "error": "Analysis failed",
  "details": "BigQuery connection error"
}
```

## Rate Limits

- **Free Tier**: 10 requests per hour
- **Professional Tier**: 100 requests per hour
- **Enterprise Tier**: 1000 requests per hour

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248000
```

## SDKs and Libraries

### Python

```python
import requests

class FDICAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.fdic-analyzer.ncrc.org"
    
    def analyze(self, counties, years):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = {"counties": counties, "years": years}
        
        response = requests.post(
            f"{self.base_url}/api/v1/analyze",
            headers=headers,
            json=data
        )
        return response.json()
    
    def get_status(self, job_id):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.get(
            f"{self.base_url}/api/v1/status/{job_id}",
            headers=headers
        )
        return response.json()
```

### JavaScript

```javascript
class FDICAnalyzer {
    constructor(apiKey) {
        this.apiKey = apiKey;
        this.baseUrl = 'https://api.fdic-analyzer.ncrc.org';
    }
    
    async analyze(counties, years) {
        const response = await fetch(`${this.baseUrl}/api/v1/analyze`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.apiKey}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ counties, years })
        });
        return response.json();
    }
    
    async getStatus(jobId) {
        const response = await fetch(`${this.baseUrl}/api/v1/status/${jobId}`, {
            headers: {
                'Authorization': `Bearer ${this.apiKey}`
            }
        });
        return response.json();
    }
}
```

## Webhooks

You can configure webhooks to receive notifications when analysis jobs complete.

### Webhook Configuration

```json
{
  "webhook_url": "https://your-app.com/webhooks/fdic-analyzer",
  "events": ["analysis.completed", "analysis.failed"],
  "secret": "your-webhook-secret"
}
```

### Webhook Payload

```json
{
  "event": "analysis.completed",
  "job_id": "job_12345",
  "timestamp": "2024-01-15T10:25:00Z",
  "data": {
    "counties": ["Cook County, Illinois"],
    "years": [2020, 2021, 2022],
    "download_url": "https://api.fdic-analyzer.ncrc.org/download/job_12345"
  }
}
```

## Data Schema

### Report Metadata

```json
{
  "analysis_id": "job_12345",
  "counties": ["Cook County, Illinois"],
  "years": [2020, 2021, 2022],
  "total_records": 150,
  "total_banks": 25,
  "generated_at": "2024-01-15T10:25:00Z",
  "ai_analysis_included": true,
  "file_size": {
    "excel": 245760,
    "pdf": 512000
  }
}
```

## Support

For API support and questions:
- Email: api-support@ncrc.org
- Documentation: https://docs.fdic-analyzer.ncrc.org
- GitHub Issues: https://github.com/jadedlebi/fdic-branch-analyzer/issues 