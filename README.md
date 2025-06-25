# AI-Assisted FDIC Bank Branch Analysis System

A comprehensive, AI-powered system for analyzing FDIC bank branch data using BigQuery and generating professional Excel and PDF reports with AI insights.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/fdic-branch-analyzer.svg)](https://badge.fury.io/py/fdic-branch-analyzer)

## 🚀 Quick Start

### Install & Run in 3 Steps

```bash
# 1. Install (choose your platform)
curl -sSL https://raw.githubusercontent.com/yourusername/fdic-branch-analyzer/main/install.sh | bash
# OR download and run install.bat (Windows)

# 2. Configure credentials
cp config_template.txt .env
# Edit .env with your BigQuery and AI API credentials

# 3. Run analysis
fdic-analyzer
```

**That's it!** Follow the prompts to analyze any county's bank branch data.

## 📊 What You Get

- **📈 Market Analysis**: Bank concentration, market share trends
- **🏘️ Community Impact**: LMI and minority tract coverage analysis  
- **🤖 AI Insights**: Executive summaries and strategic recommendations
- **📋 Professional Reports**: Excel data tables + PDF narratives
- **📅 Multi-Year Trends**: 2017-2024 analysis capabilities

## 🏗️ Project Structure

```
branch_ai/
├── main.py                          # Entry point
├── setup.py                         # Package configuration
├── install.sh                       # Unix installation script
├── install.bat                      # Windows installation script
├── config_template.txt              # Credentials template
├── QUICKSTART.md                    # Quick start guide
├── src/                            # Source code
│   ├── core/                       # Core application logic
│   ├── utils/                      # Utility modules
│   ├── analysis/                   # AI analysis modules
│   └── reporting/                  # Report generation modules
├── config/                         # Configuration files
├── data/                          # Data directories
├── docs/                          # Documentation and templates
├── tests/                         # Test files
└── scripts/                       # Utility scripts
```

## 🛠️ Installation Options

### Option 1: Automated Installation (Recommended)

**macOS/Linux:**
```bash
curl -sSL https://raw.githubusercontent.com/yourusername/fdic-branch-analyzer/main/install.sh | bash
```

**Windows:**
```cmd
# Download and run install.bat
```

### Option 2: Manual Installation

```bash
# Clone and setup
git clone https://github.com/yourusername/fdic-branch-analyzer.git
cd fdic-branch-analyzer
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate.bat
pip install -r requirements.txt
pip install -e .
```

### Option 3: PyPI Installation (Coming Soon)

```bash
pip install fdic-branch-analyzer
```

## 🔐 Setup Credentials

1. **Copy the template:**
   ```bash
   cp config_template.txt .env
   ```

2. **Add your credentials to `.env`:**
   ```bash
   # BigQuery (from Google Cloud Console)
   BQ_PROJECT_ID=your-project-id
   BQ_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n..."
   BQ_CLIENT_EMAIL=your-service@your-project.iam.gserviceaccount.com
   
   # AI Provider (choose one)
   CLAUDE_API_KEY=sk-ant-api03-...  # Recommended
   # OPENAI_API_KEY=sk-...          # Alternative
   ```

## 🎯 Usage Examples

### Single County Analysis
```bash
fdic-analyzer
# Enter: montgomery county, maryland
# Enter: 2020,2021,2022
```

### Multi-County Analysis
```bash
fdic-analyzer
# Enter: montgomery county, maryland; cook county, illinois
# Enter: all
```

### Specific Year Range
```bash
fdic-analyzer
# Enter: queens county, new york
# Enter: 2018,2019,2020,2021
```

## 📋 Prerequisites

- **Python 3.9+**
- **BigQuery access** (Google Cloud account)
- **AI API key** (Claude or OpenAI)

## 🤖 AI Providers

### Claude (Recommended)
- **Model**: Claude 3.5 Sonnet
- **Features**: Comprehensive analysis, detailed insights
- **Setup**: Get API key from [console.anthropic.com](https://console.anthropic.com)

### GPT-4 (Alternative)
- **Model**: GPT-4
- **Features**: Alternative AI analysis
- **Setup**: Get API key from [platform.openai.com](https://platform.openai.com)

## 📁 Directory Details

### `src/` - Source Code
- **`core/`**: Main application logic and workflow orchestration
- **`utils/`**: BigQuery utilities, county matching, and helper functions
- **`analysis/`**: AI analysis modules and GPT/Claude integration
- **`reporting/`**: Excel and PDF report generation

### `config/` - Configuration
- **`config.py`**: Central configuration file with all settings
- Paths, AI models, BigQuery settings, and report configuration

### `data/` - Data Management
- **`raw/`**: Original data files and samples
- **`processed/`**: Intermediate processed data
- **`reports/`**: Generated Excel and PDF reports

### `docs/` - Documentation
- **`prompts/`**: AI prompt templates
- **`query_templates/`**: SQL query templates
- **`*.md`**: Comprehensive documentation

## 🧪 Testing

```bash
# Quick tests
make test-quick

# Full test suite
make test

# Run demo
make demo
```

## 🔧 Development

```bash
# Setup development environment
make setup-dev

# Run all checks
make check

# Build package
make build
```

## 🐛 Troubleshooting

### Common Issues

**"BigQuery credentials not found"**
- Check your `.env` file exists and has correct values
- Verify your service account has BigQuery access

**"AI API key not found"**
- Add your API key to `.env`
- Check your API key is valid and has credits

**"Python not found"**
- Install Python 3.9+ from [python.org](https://python.org)
- Ensure Python is in your PATH

### Getting Help

- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)
- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/fdic-branch-analyzer/issues)
- **Setup Guide**: [docs/CLAUDE_SETUP.md](docs/CLAUDE_SETUP.md)

## 📈 Features

### Core Functionality
- **Dynamic Input**: Interactive prompts for counties and years
- **Multi-County Analysis**: Support for multiple counties in a single report
- **Year Range Analysis**: Flexible year selection (2017-2024)
- **County Clarification**: Smart county name matching and disambiguation

### Data Analysis
- **BigQuery Integration**: Direct querying of FDIC Summary of Deposits data
- **Market Share Analysis**: Bank concentration and market share calculations
- **Community Impact**: LMI and MMCT tract analysis
- **Trend Analysis**: Year-over-year growth and decline patterns

### AI-Powered Insights
- **Executive Summary**: AI-generated executive overview
- **Key Findings**: Automated identification of important trends
- **Strategic Analysis**: Bank strategy and community impact insights
- **Conclusions**: AI-powered strategic implications

### Report Generation
- **Excel Reports**: Comprehensive data tables and analysis
- **PDF Reports**: Professional, formatted reports with AI insights
- **Modern Formatting**: Clean, readable presentation with proper sections
- **Multiple Formats**: Both statistical and narrative analysis

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Follow the established directory structure
4. Add tests for new functionality
5. Update documentation as needed
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational and research purposes. Please ensure compliance with:
- FDIC data usage policies
- API terms of service
- Local data protection regulations

## 🎉 Support

If you find this tool helpful, please:
- ⭐ Star the repository
- 🐛 Report issues
- 💡 Suggest improvements
- 📖 Share with colleagues

---

**Happy analyzing! 📊** 