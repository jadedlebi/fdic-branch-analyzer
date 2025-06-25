# 🚀 Quick Start Guide

Get the FDIC Branch Analyzer up and running in minutes!

## 📋 Prerequisites

- **Python 3.9 or higher**
- **BigQuery access** (Google Cloud account)
- **AI API key** (Claude or OpenAI)

## ⚡ Quick Installation

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
# Clone the repository
git clone https://github.com/yourusername/fdic-branch-analyzer.git
cd fdic-branch-analyzer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

## 🔐 Setup Credentials

1. **Copy the configuration template:**
   ```bash
   cp config_template.txt .env
   ```

2. **Edit `.env` with your credentials:**
   - **BigQuery**: Copy values from your service account JSON
   - **AI Provider**: Add your Claude or OpenAI API key

3. **Example `.env` file:**
   ```bash
   BQ_PROJECT_ID=my-project-123
   BQ_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n..."
   BQ_CLIENT_EMAIL=my-service@my-project.iam.gserviceaccount.com
   CLAUDE_API_KEY=sk-ant-api03-...
   ```

## 🎯 Run Your First Analysis

```bash
# Activate environment (if not already active)
source venv/bin/activate

# Run the analyzer
fdic-analyzer
```

**Follow the prompts:**
- Enter counties: `montgomery county, maryland`
- Enter years: `all` (or specific years like `2020,2021,2022`)

## 📊 View Results

Your reports will be saved in `data/reports/`:
- **Excel file**: Detailed data tables
- **PDF file**: Professional analysis with AI insights

## 🆘 Need Help?

- **Documentation**: [README.md](README.md)
- **Issues**: [GitHub Issues](https://github.com/yourusername/fdic-branch-analyzer/issues)
- **Setup Guide**: [docs/CLAUDE_SETUP.md](docs/CLAUDE_SETUP.md)

## 🔧 Troubleshooting

**"BigQuery credentials not found"**
- Check your `.env` file exists and has correct values
- Verify your service account has BigQuery access

**"AI API key not found"**
- Add your API key to `.env`
- Check your API key is valid and has credits

**"Python not found"**
- Install Python 3.9+ from [python.org](https://python.org)
- Ensure Python is in your PATH

## 🎉 You're Ready!

The analyzer will generate comprehensive reports with:
- ✅ Market share analysis
- ✅ Community impact metrics
- ✅ AI-powered insights
- ✅ Professional formatting
- ✅ Multi-year trends

Happy analyzing! 📈 