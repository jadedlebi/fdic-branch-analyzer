from flask import Flask, render_template, request, jsonify, send_file, session, Response
import os
import tempfile
import zipfile
from datetime import datetime
import traceback
from src.core.main import run_analysis
import sys
from src.utils.county_reference import get_all_counties
from src.utils.run_logger import run_logger, get_user_info
import uuid
import threading
import time
import json

# Set up Google Cloud credentials for BigQuery logging
try:
    from scripts.setup_gcp_credentials import setup_environment
    setup_environment()
except ImportError:
    print("Warning: Could not set up GCP credentials for logging")

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import config
from config import config

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')

job_progress = {}  # job_id: {"step": str, "percent": int, "done": bool, "error": str or None}

@app.route('/')
def index():
    """Main page with the analysis form"""
    return render_template('index.html')

@app.route('/progress/<job_id>')
def progress(job_id):
    def event_stream():
        last_percent = -1
        while True:
            progress = job_progress.get(job_id, {})
            percent = progress.get("percent", 0)
            step = progress.get("step", "Starting...")
            done = progress.get("done", False)
            error = progress.get("error", None)
            if percent != last_percent or done or error:
                yield f"data: {{\"percent\": {percent}, \"step\": \"{step}\", \"done\": {str(done).lower()}, \"error\": {json.dumps(error) if error else 'null'}}}\n\n"
                last_percent = percent
            if done or error:
                break
            time.sleep(0.5)
    return Response(event_stream(), mimetype="text/event-stream")

@app.route('/analyze', methods=['POST'])
def analyze():
    """Handle analysis request"""
    try:
        data = request.get_json()
        counties = data.get('counties', '').strip()
        years = data.get('years', '').strip()
        job_id = str(uuid.uuid4())
        job_progress[job_id] = {"step": "Initializing analysis...", "percent": 0, "done": False, "error": None}
        
        if not counties or not years:
            return jsonify({'error': 'Please provide both counties and years'}), 400
        
        # Get user information for logging
        user_info = get_user_info(request)
        
        # Parse counties and years for logging
        counties_list = [c.strip() for c in counties.split(';') if c.strip()]
        years_list = []
        if years.lower() == 'all':
            years_list = list(range(2017, 2025))
        else:
            years_list = [int(y.strip()) for y in years.split(',') if y.strip().isdigit()]
        
        # Start run logging
        run_id = run_logger.start_run(
            counties=counties_list,
            years=years_list,
            interface_type="web",
            user_ip=user_info.get('ip'),
            user_agent=user_info.get('user_agent'),
            session_id=session.get('session_id', str(uuid.uuid4()))
        )
        
        # Store in session for download
        session['counties'] = counties
        session['years'] = years
        session['run_id'] = run_id
        
        def run_job():
            try:
                # Step 1: Connecting to database
                job_progress[job_id].update({"step": "Connecting to database...", "percent": 10})
                # No-op: connection is handled in run_analysis

                # Step 2: Querying branch data
                job_progress[job_id].update({"step": "Querying branch data...", "percent": 30})

                # Step 3: Processing county information
                job_progress[job_id].update({"step": "Processing county information...", "percent": 50})

                # Step 4: Generating AI insights
                job_progress[job_id].update({"step": "Generating AI insights...", "percent": 70})

                # Step 5: Creating Excel report
                job_progress[job_id].update({"step": "Creating Excel report...", "percent": 85})

                # Step 6: Generating PDF report
                job_progress[job_id].update({"step": "Generating PDF report...", "percent": 95})

                # Actually run the analysis pipeline
                result = run_analysis(counties, years, run_id)

                if not result.get('success'):
                    error_msg = result.get('error', 'Unknown error')
                    job_progress[job_id].update({"error": error_msg, "done": True})
                    # Log the failed run
                    run_logger.end_run(run_id, success=False, error_message=error_msg)
                    return

                # Step 7: Finalizing
                job_progress[job_id].update({"step": "Finalizing analysis...", "percent": 100, "done": True})
                
                # Log the successful run
                run_logger.end_run(run_id, success=True)
            except Exception as e:
                error_msg = str(e)
                job_progress[job_id].update({"error": error_msg, "done": True})
                # Log the failed run
                run_logger.end_run(run_id, success=False, error_message=error_msg)

        threading.Thread(target=run_job).start()

        return jsonify({"job_id": job_id})
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }), 500

@app.route('/download')
def download():
    """Download the generated reports"""
    try:
        counties = session.get('counties')
        years = session.get('years')
        
        if not counties or not years:
            return jsonify({'error': 'No analysis data found'}), 400
        
        # Create a temporary directory for the zip file
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, 'fdic_analysis_reports.zip')
            
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                # Add Excel file - check both possible locations
                excel_paths = [
                    os.path.join('data', 'reports', 'fdic_branch_analysis.xlsx'),
                    os.path.join('data', 'output', 'fdic_branch_analysis.xlsx')
                ]
                
                excel_found = False
                for excel_path in excel_paths:
                    if os.path.exists(excel_path):
                        zipf.write(excel_path, 'fdic_branch_analysis.xlsx')
                        excel_found = True
                        break
                
                # Add PDF file - check both possible locations
                pdf_paths = [
                    os.path.join('data', 'reports', 'fdic_branch_analysis.pdf'),
                    os.path.join('data', 'output', 'fdic_branch_analysis.pdf')
                ]
                
                pdf_found = False
                for pdf_path in pdf_paths:
                    if os.path.exists(pdf_path):
                        zipf.write(pdf_path, 'fdic_branch_analysis.pdf')
                        pdf_found = True
                        break
                
                # If no files found, return error
                if not excel_found and not pdf_found:
                    return jsonify({
                        'success': False,
                        'error': 'No report files found. Please run the analysis first.'
                    }), 404
            
            return send_file(
                zip_path,
                as_attachment=True,
                download_name=f'fdic_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip',
                mimetype='application/zip'
            )
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Download failed: {str(e)}'
        }), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/counties')
def counties():
    """Return a list of all available counties for the dropdown/autocomplete."""
    counties = get_all_counties()
    print("PROJECT_ID:", config.PROJECT_ID)
    print("Counties fetched:", len(counties))
    print("Counties sample:", counties[:5])
    sys.stdout.flush()  # Ensure logs are flushed
    return jsonify(counties)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080) 