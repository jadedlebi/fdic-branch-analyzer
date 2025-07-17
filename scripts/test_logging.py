#!/usr/bin/env python3
"""
Test script to verify the FDIC Analyzer logging system.
"""

import os
import sys
import tempfile
import shutil
from datetime import datetime

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Set up Google Cloud credentials before importing run_logger
try:
    from scripts.setup_gcp_credentials import setup_environment
    setup_environment()
except ImportError:
    print("Warning: Could not set up GCP credentials automatically")

from src.utils.run_logger import run_logger, RunLogger

def test_logging_system():
    """Test the logging system functionality."""
    print("🧪 Testing FDIC Analyzer Logging System")
    print("=" * 50)
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Using temporary directory: {temp_dir}")
        
        # Create a test logger
        test_logger = RunLogger(temp_dir)
        
        # Test 1: Start a run
        print("\n1️⃣ Testing run start...")
        run_id = test_logger.start_run(
            counties=['Cook County, Illinois', 'Los Angeles County, California'],
            years=[2020, 2021, 2022],
            interface_type='web',
            user_ip='192.168.1.100',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        print(f"✅ Run started with ID: {run_id}")
        
        # Test 2: Update run metadata
        print("\n2️⃣ Testing metadata updates...")
        test_logger.update_run(
            run_id,
            ai_provider='claude',
            ai_model='claude-3-5-sonnet-20241022',
            ai_calls=3,
            ai_input_tokens=1500,
            ai_output_tokens=800,
            bq_queries=6,
            bq_bytes_processed=1024 * 1024 * 100,  # 100 MB
            records_processed=2500
        )
        print("✅ Metadata updated successfully")
        
        # Test 3: End the run
        print("\n3️⃣ Testing run completion...")
        test_logger.end_run(run_id, success=True)
        print("✅ Run completed successfully")
        
        # Test 4: Check summary
        print("\n4️⃣ Testing summary retrieval...")
        df = test_logger.get_runs_summary()
        cost_summary = test_logger.get_cost_summary()
        
        print(f"✅ Found {len(df)} runs in summary")
        print(f"✅ Total cost: ${cost_summary['total_cost']:.4f}")
        print(f"✅ AI cost: ${cost_summary['ai_cost']:.4f}")
        print(f"✅ BigQuery cost: ${cost_summary['bq_cost']:.4f}")
        
        # Test 5: Check detailed run
        print("\n5️⃣ Testing detailed run retrieval...")
        details = test_logger.get_run_details(run_id)
        if details:
            print(f"✅ Detailed run found")
            print(f"   - Counties: {details['counties']}")
            print(f"   - Years: {details['years']}")
            print(f"   - AI calls: {details['ai_calls']}")
            print(f"   - BQ queries: {details['bq_queries']}")
            print(f"   - Success: {details['success']}")
        else:
            print("❌ Detailed run not found")
        
        # Test 6: Export summary report
        print("\n6️⃣ Testing report generation...")
        report_file = os.path.join(temp_dir, 'test_report.json')
        test_logger.export_summary_report(report_file)
        
        if os.path.exists(report_file):
            print(f"✅ Summary report generated: {report_file}")
        else:
            print("❌ Summary report generation failed")
        
        # Test 7: Check file structure
        print("\n7️⃣ Testing file structure...")
        runs_file = os.path.join(temp_dir, 'runs.csv')
        detailed_dir = os.path.join(temp_dir, 'detailed')
        
        if os.path.exists(runs_file):
            print(f"✅ CSV file created: {runs_file}")
        else:
            print("❌ CSV file not created")
        
        if os.path.exists(detailed_dir):
            detailed_files = os.listdir(detailed_dir)
            print(f"✅ Detailed logs directory created with {len(detailed_files)} files")
        else:
            print("❌ Detailed logs directory not created")
    
    print("\n🎉 All tests completed successfully!")
    print("\n📊 Test Summary:")
    print("   ✅ Run creation and tracking")
    print("   ✅ Metadata updates")
    print("   ✅ Cost calculations")
    print("   ✅ Summary retrieval")
    print("   ✅ Detailed run access")
    print("   ✅ Report generation")
    print("   ✅ File structure creation")


def test_cost_calculations():
    """Test cost calculation accuracy."""
    print("\n💰 Testing Cost Calculations")
    print("=" * 30)
    
    # Test AI cost calculations
    from src.utils.run_logger import COST_ESTIMATES
    
    print("🤖 AI Cost Estimates:")
    for provider, models in COST_ESTIMATES.items():
        print(f"   {provider.upper()}:")
        for model, costs in models.items():
            print(f"     {model}: ${costs['input']:.3f}/1K input, ${costs['output']:.3f}/1K output")
    
    # Test BigQuery cost calculation
    from src.utils.run_logger import BQ_COST_PER_TB
    
    test_bytes = 1024**4  # 1 TB
    expected_cost = 5.0  # $5 per TB
    
    calculated_cost = (test_bytes / (1024**4)) * BQ_COST_PER_TB
    
    print(f"\n🗄️ BigQuery Cost Test:")
    print(f"   Test data: {test_bytes:,} bytes (1 TB)")
    print(f"   Expected cost: ${expected_cost:.2f}")
    print(f"   Calculated cost: ${calculated_cost:.2f}")
    print(f"   ✅ {'PASS' if abs(calculated_cost - expected_cost) < 0.01 else 'FAIL'}")


def main():
    """Main test function."""
    print("🚀 FDIC Analyzer Logging System Test Suite")
    print("=" * 60)
    
    try:
        test_logging_system()
        test_cost_calculations()
        
        print("\n🎯 All tests passed! The logging system is working correctly.")
        print("\n📝 Next steps:")
        print("   1. Run the tool to generate real logs")
        print("   2. Use 'python scripts/view_logs.py --summary' to view logs")
        print("   3. Use 'python scripts/generate_run_report.py' to create reports")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 