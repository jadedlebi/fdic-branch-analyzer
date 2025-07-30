# FDIC Branch Analyzer

A comprehensive banking market intelligence platform that analyzes FDIC Summary of Deposits (SOD) data to provide detailed insights into branch networks, market share dynamics, and banking trends across counties and time periods.

## 🎯 Purpose

This tool is designed for banking analysts, researchers, and policymakers to:

- **Analyze Branch Networks**: Track branch presence, closures, and openings across geographic markets
- **Calculate Market Share**: Determine bank market dominance and competitive positioning
- **Identify Trends**: Spot patterns in banking consolidation, expansion, and strategic shifts
- **Generate Professional Reports**: Create Excel and PDF reports with AI-powered insights
- **Support Policy Analysis**: Provide data-driven insights for community reinvestment and banking policy research

## 🚀 Quick Start

1. **Enter Counties**: 
   - Single county: `Cook County, Illinois`
   - Multiple counties: `Cook County, Illinois; Los Angeles County, California`

2. **Enter Years**:
   - Specific years: `2020,2021,2022`
   - All years: `all` (2017-2024)

3. **Generate Analysis**: Click "Generate Analysis" and wait for processing

4. **Download Reports**: Get a ZIP file containing Excel and PDF reports

## 📊 Analysis Capabilities

### Data Analysis
- **Branch Statistics**: Total branches, closures, openings, and net changes
- **Market Share Calculations**: Bank dominance and competitive positioning
- **Year-over-Year Comparisons**: Growth trends and market evolution
- **Bank Rankings**: Top players by branch count and market share
- **Geographic Coverage**: Multi-county analysis with comparative insights

### AI-Powered Insights
- **Executive Summaries**: Key findings and market overview
- **Trend Analysis**: Banking consolidation and expansion patterns
- **Strategic Insights**: Bank strategies and competitive dynamics
- **Community Impact**: Effects on local banking access and competition
- **Policy Implications**: Regulatory and community reinvestment considerations

### Professional Reporting
- **Excel Reports**: Raw data with detailed statistics and calculations
- **PDF Reports**: Executive summaries with charts, tables, and narrative analysis
- **Visual Analytics**: Charts showing trends, market share, and comparisons
- **Comprehensive Coverage**: All FDIC-regulated institutions and branches

## 🏗️ Project Structure

```
fdic-branch-analyzer/
├── web/                    # GitHub Pages static site
│   ├── index.html         # Main interface
│   ├── css/style.css      # Styling
│   ├── js/app.js          # Frontend logic
│   └── _config.yml        # GitHub Pages config
├── src/                   # Core application
│   ├── core/main.py       # Main orchestration
│   ├── utils/             # Utilities
│   ├── analysis/          # AI analysis
│   └── reporting/         # Report generation
├── config/                # Configuration
├── docs/                  # Documentation
│   ├── README.md          # User guide
│   ├── API.md             # API documentation
│   └── DEPLOYMENT.md      # Deployment guide
├── scripts/               # Automation scripts
│   └── deploy/            # Deployment scripts
└── data/                  # Data storage (gitignored)
```

## 🛠️ Technical Stack

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Backend**: Python 3.8+, Flask
- **Data Source**: FDIC Summary of Deposits (SOD) via BigQuery
- **AI Engine**: Claude 3.5 Sonnet for intelligent analysis
- **Analysis Engine**: pandas, matplotlib, reportlab
- **Deployment**: GitHub Pages, Docker, Cloud platforms

## 🔧 Development Setup

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

## 🚀 Deployment

### GitHub Pages (Recommended)
```bash
./scripts/deploy/deploy.sh
```

### Docker
```bash
docker build -t fdic-analyzer .
docker run -p 5000:5000 fdic-analyzer
```

### Cloud Platforms
See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed deployment guides.

## 🔒 Security

- All credentials are stored in environment variables
- No sensitive data is committed to the repository
- BigQuery access is restricted to authorized users
- API keys are encrypted and secure

## 📚 Documentation

- **[User Guide](docs/README.md)** - How to use the application
- **[API Documentation](docs/API.md)** - For developers and integrations
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment instructions

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
- [Issues & Support](https://github.com/jadedlebi/fdic-branch-analyzer/issues)

## 📞 Support

For questions or support:
- Create an issue on GitHub
- Contact the NCRC team
- Check the documentation in the `docs/` folder

---

**Built with ❤️ by NCRC for better banking market intelligence** 