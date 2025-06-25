#!/usr/bin/env python3
"""
Test script to verify all components of the AI-assisted report generator are working.
"""

import os
import sys
from config import OPENAI_API_KEY, BQ_CREDENTIALS_PATH, PROJECT_ID

def test_config():
    """Test configuration settings."""
    print("🔧 Testing configuration...")
    
    # Check OpenAI API key
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY not found in .env file")
        return False
    else:
        print("✅ OpenAI API key found")
    
    # Check BigQuery credentials
    if not os.path.exists(BQ_CREDENTIALS_PATH):
        print(f"❌ BigQuery credentials file not found: {BQ_CREDENTIALS_PATH}")
        return False
    else:
        print(f"✅ BigQuery credentials found: {BQ_CREDENTIALS_PATH}")
    
    # Check project ID
    if not PROJECT_ID:
        print("❌ PROJECT_ID not configured")
        return False
    else:
        print(f"✅ Project ID configured: {PROJECT_ID}")
    
    return True

def test_dependencies():
    """Test that all required packages are installed."""
    print("\n📦 Testing dependencies...")
    
    required_packages = [
        'openai',
        'google.cloud.bigquery',
        'pandas',
        'openpyxl',
        'dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'google.cloud.bigquery':
                import google.cloud.bigquery
            elif package == 'dotenv':
                import dotenv
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nInstall missing packages with: pip install {' '.join(missing_packages)}")
        return False
    
    return True

def test_gpt():
    """Test GPT API connection."""
    print("\n🤖 Testing GPT API...")
    
    try:
        from gpt_utils import ask_gpt
        response = ask_gpt("Hello! Please respond with 'GPT is working' if you can see this message.")
        print(f"✅ GPT API working - Response: {response[:50]}...")
        return True
    except Exception as e:
        print(f"❌ GPT API test failed: {e}")
        return False

def test_bigquery():
    """Test BigQuery connection."""
    print("\n🔍 Testing BigQuery connection...")
    
    try:
        from bq_utils import test_connection
        if test_connection():
            print("✅ BigQuery connection successful")
            return True
        else:
            print("❌ BigQuery connection failed")
            return False
    except Exception as e:
        print(f"❌ BigQuery test failed: {e}")
        return False

def test_file_structure():
    """Test that all required files exist."""
    print("\n📁 Testing file structure...")
    
    required_files = [
        'prompts/reporting_prompt.txt',
        'query_templates/branch_report.sql',
        'main.py',
        'config.py',
        'gpt_utils.py',
        'bq_utils.py',
        'report_builder.py'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - not found")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\nMissing files: {missing_files}")
        return False
    
    return True

def main():
    """Run all tests."""
    print("🧪 Running setup tests for AI-assisted report generator...\n")
    
    tests = [
        ("Configuration", test_config),
        ("Dependencies", test_dependencies),
        ("File Structure", test_file_structure),
        ("GPT API", test_gpt),
        ("BigQuery", test_bigquery)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your setup is ready to use.")
        print("Run 'python main.py' to generate your first report.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please fix the issues above before running the main script.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 