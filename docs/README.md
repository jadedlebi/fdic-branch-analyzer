# FDIC Branch Analyzer

AI-powered banking market intelligence platform for analyzing FDIC branch data with comprehensive insights and professional reporting.

## 🌟 Features

- **Comprehensive Data Analysis**: Detailed branch statistics, market share analysis, and growth trends
- **AI-Powered Insights**: Claude AI-generated analysis of banking strategies and market dynamics
- **Professional Reports**: Excel spreadsheets and PDF reports with charts, tables, and narrative analysis
- **Multi-County Support**: Analyze multiple counties simultaneously
- **Historical Data**: Access data from 2017-2024
- **User-Friendly Interface**: Modern, responsive web interface

## 🚀 Quick Start

1. **Enter Counties**: 
   - Single county: `Cook County, Illinois`
   - Multiple counties: `Cook County, Illinois; Los Angeles County, California`

2. **Enter Years**:
   - Specific years: `2020,2021,2022`
   - All years: `all` (2017-2024)

3. **Generate Analysis**: Click "Generate Analysis" and wait for processing

4. **Download Reports**: Get a ZIP file containing Excel and PDF reports

## 📊 What You'll Get

### Excel Report
- Raw branch data with detailed statistics
- Market share calculations
- Year-over-year comparisons
- Bank rankings and analysis

### PDF Report
- Executive summary with key findings
- AI-generated insights and analysis
- Professional charts and tables
- Strategic recommendations
- Market dynamics overview

## 🛠️ Technical Details

- **Data Source**: FDIC Summary of Deposits (SOD) via BigQuery
- **AI Engine**: Claude 3.5 Sonnet for intelligent analysis
- **Analysis Engine**: Python with pandas, matplotlib, and reportlab
- **Web Interface**: Modern HTML5, CSS3, and JavaScript

## 🔧 Setup for Developers

### Prerequisites
- Python 3.8+
- BigQuery access
- Claude API key

### Installation
```bash
git clone https://github.com/jadedlebi/fdic-branch-analyzer.git
cd fdic-branch-analyzer
pip install -r requirements.txt
```

### Environment Setup
Create a `.env` file with:
```env
# BigQuery Credentials
BQ_TYPE=service_account
BQ_PROJECT_ID=your-project-id
BQ_PRIVATE_KEY=your-private-key
BQ_CLIENT_EMAIL=your-client-email

# AI API Keys
CLAUDE_API_KEY=your-claude-key
OPENAI_API_KEY=your-openai-key
```

### Running Locally
```bash
python run_web.py
```
Then visit `http://127.0.0.1:5050`

## 📁 Project Structure

```
fdic-branch-analyzer/
├── web/                    # GitHub Pages static site
│   ├── index.html         # Main interface
│   ├── css/style.css      # Styling
│   └── js/app.js          # Frontend logic
├── src/                   # Core application
│   ├── core/main.py       # Main orchestration
│   ├── utils/             # Utilities
│   ├── analysis/          # AI analysis
│   └── reporting/         # Report generation
├── config/                # Configuration
├── docs/                  # Documentation
└── data/                  # Data storage
```

## 🔒 Security

- All credentials are stored in environment variables
- No sensitive data is committed to the repository
- BigQuery access is restricted to authorized users
- API keys are encrypted and secure

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is developed by NCRC (National Community Reinvestment Coalition) for banking market analysis and research purposes.

## 👥 Authors

- **Jad Edlebi** - NCRC
- **Jason Richardson** - NCRC

## 🔗 Links

- [GitHub Repository](https://github.com/jadedlebi/fdic-branch-analyzer)
- [NCRC Website](https://ncrc.org)
- [API Documentation](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## 📞 Support

For questions or support, please contact the NCRC team or create an issue on GitHub. 