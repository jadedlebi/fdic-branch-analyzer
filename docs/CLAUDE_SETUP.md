# Claude Integration Setup Guide

This guide explains how to switch from GPT-4 to Claude for AI-powered analysis in the bank branch report generator.

## 🔧 Configuration Changes

### 1. Update Configuration File

The system is already configured to use Claude by default. In `config.py`, you can see:

```python
# AI Model Configuration
AI_PROVIDER = "claude"  # Change this to "openai" if you want to use GPT-4

# Claude Configuration
CLAUDE_MODEL = "claude-3-5-sonnet-20241022"  # Latest Claude model
```

### 2. Set Up Claude API Key

You need to get a Claude API key from Anthropic:

1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in to your account
3. Navigate to "API Keys" section
4. Create a new API key
5. Copy the API key

### 3. Add API Key to Environment

Create or update your `.env` file in the project root:

```bash
# .env file
CLAUDE_API_KEY=your_claude_api_key_here
```

Or set it as an environment variable:

```bash
export CLAUDE_API_KEY=your_claude_api_key_here
```

## 🧪 Testing the Integration

Run the test script to verify Claude integration:

```bash
python test_claude_integration.py
```

This will test:
- Basic AI calls
- AI Analyzer initialization
- Executive summary generation
- Key findings generation
- Trends analysis
- Bank strategies analysis
- Community impact analysis
- Conclusion generation

## 🔄 Switching Between AI Providers

### To use Claude (default):
```python
AI_PROVIDER = "claude"
```

### To use GPT-4:
```python
AI_PROVIDER = "openai"
```

Make sure you have the appropriate API key set:
- For Claude: `CLAUDE_API_KEY`
- For OpenAI: `OPENAI_API_KEY`

## 📊 Available Claude Models

The system is configured to use `claude-3-5-sonnet-20241022`, which is the latest and most capable Claude model. You can change this in `config.py`:

```python
CLAUDE_MODEL = "claude-3-5-sonnet-20241022"  # Latest model
# Other options:
# CLAUDE_MODEL = "claude-3-opus-20240229"    # Most capable
# CLAUDE_MODEL = "claude-3-sonnet-20240229"  # Balanced
# CLAUDE_MODEL = "claude-3-haiku-20240307"   # Fastest
```

## 🚀 Running the Full Pipeline

Once configured, run the main script as usual:

```bash
python main.py
```

The system will automatically use Claude for all AI analysis, including:
- Executive summaries
- Key findings
- Trend analysis
- Bank strategy insights
- Community impact analysis
- Strategic conclusions

## 💡 Benefits of Using Claude

1. **Enhanced Reasoning**: Claude often provides more detailed and nuanced analysis
2. **Better Context Understanding**: Improved comprehension of complex financial data
3. **Consistent Output**: More reliable formatting and structure
4. **Cost Effective**: Often more cost-effective than GPT-4 for similar quality
5. **Safety**: Built with strong safety and ethical considerations

## 🔍 Troubleshooting

### Common Issues:

1. **API Key Not Found**
   - Ensure `CLAUDE_API_KEY` is set in your `.env` file or environment
   - Check that the key is valid and active

2. **Import Errors**
   - Make sure `anthropic` package is installed: `pip install anthropic`

3. **Rate Limiting**
   - Claude has rate limits; if you hit them, wait a moment and retry

4. **Model Not Available**
   - Ensure you're using a valid model name
   - Check Anthropic's documentation for current model availability

### Getting Help:

- Check the test script output for specific error messages
- Verify your API key is working with a simple test call
- Ensure you have the latest version of the `anthropic` package

## 📈 Performance Comparison

Both Claude and GPT-4 provide excellent analysis, but you may notice:

- **Claude**: More detailed explanations, better reasoning chains
- **GPT-4**: Faster response times, more creative insights

The choice between them often comes down to personal preference and specific use case requirements. 