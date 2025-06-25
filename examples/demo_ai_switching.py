#!/usr/bin/env python3
"""
Demonstration script showing how to switch between AI providers.
This script shows the configuration and testing for both Claude and OpenAI.
"""

import os
import sys
from config import AI_PROVIDER, OPENAI_API_KEY, CLAUDE_API_KEY

def show_current_config():
    """Show the current AI provider configuration."""
    print("🔧 Current AI Configuration:")
    print(f"   Provider: {AI_PROVIDER.upper()}")
    
    if AI_PROVIDER == "openai":
        print(f"   Model: gpt-4")
        print(f"   API Key: {'✅ Set' if OPENAI_API_KEY else '❌ Not set'}")
    elif AI_PROVIDER == "claude":
        print(f"   Model: claude-3-5-sonnet-20241022")
        print(f"   API Key: {'✅ Set' if CLAUDE_API_KEY else '❌ Not set'}")
    
    print()

def show_switching_instructions():
    """Show instructions for switching between AI providers."""
    print("🔄 How to Switch AI Providers:")
    print()
    print("1. Edit config.py and change AI_PROVIDER:")
    print("   # For Claude:")
    print("   AI_PROVIDER = 'claude'")
    print()
    print("   # For OpenAI:")
    print("   AI_PROVIDER = 'openai'")
    print()
    print("2. Set the appropriate API key:")
    print("   # For Claude - add to .env file:")
    print("   CLAUDE_API_KEY=your_claude_api_key_here")
    print()
    print("   # For OpenAI - add to .env file:")
    print("   OPENAI_API_KEY=your_openai_api_key_here")
    print()
    print("3. Test the configuration:")
    print("   python test_claude_integration.py  # for Claude")
    print("   python test_openai_integration.py  # for OpenAI")
    print()

def show_available_models():
    """Show available models for each provider."""
    print("📊 Available Models:")
    print()
    print("🤖 Claude Models:")
    print("   - claude-3-5-sonnet-20241022 (Latest, recommended)")
    print("   - claude-3-opus-20240229 (Most capable)")
    print("   - claude-3-sonnet-20240229 (Balanced)")
    print("   - claude-3-haiku-20240307 (Fastest)")
    print()
    print("🧠 OpenAI Models:")
    print("   - gpt-4 (Most capable)")
    print("   - gpt-4-turbo (Fast and capable)")
    print("   - gpt-3.5-turbo (Fast and cost-effective)")
    print()

def show_benefits_comparison():
    """Show benefits comparison between providers."""
    print("📈 Provider Benefits Comparison:")
    print()
    print("🤖 Claude Benefits:")
    print("   ✅ Enhanced reasoning and detailed analysis")
    print("   ✅ Better context understanding")
    print("   ✅ More consistent output formatting")
    print("   ✅ Cost-effective for similar quality")
    print("   ✅ Strong safety and ethical considerations")
    print()
    print("🧠 OpenAI Benefits:")
    print("   ✅ Faster response times")
    print("   ✅ More creative insights")
    print("   ✅ Extensive model options")
    print("   ✅ Well-established API")
    print("   ✅ Good for real-time applications")
    print()

def main():
    """Main demonstration function."""
    print("🚀 AI Provider Configuration Demo")
    print("=" * 50)
    print()
    
    show_current_config()
    show_switching_instructions()
    show_available_models()
    show_benefits_comparison()
    
    print("💡 Quick Test Commands:")
    print("   # Test current configuration:")
    print("   python test_claude_integration.py")
    print()
    print("   # Run full pipeline with current AI provider:")
    print("   python main.py")
    print()
    print("   # Check if API keys are properly loaded:")
    print("   python -c \"from config import *; print(f'OpenAI: {bool(OPENAI_API_KEY)}'); print(f'Claude: {bool(CLAUDE_API_KEY)}')\"")
    print()

if __name__ == "__main__":
    main() 