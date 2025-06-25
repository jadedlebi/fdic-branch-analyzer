from flask import Flask, render_template, request, jsonify, send_file, session
import os
import tempfile
import zipfile
from datetime import datetime
import traceback
from src.core.main import run_analysis
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import config
from config import config

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')

@app.route('/')
def index():
    """Main page with the analysis form"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Handle analysis request"""
    try:
        data = request.get_json()
        counties = data.get('counties', '').strip()
        years = data.get('years', '').strip()
        
        if not counties or not years:
            return jsonify({'error': 'Please provide both counties and years'}), 400
        
        # Store in session for download
        session['counties'] = counties
        session['years'] = years
        
        # Run analysis
        result = run_analysis(counties, years)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': 'Analysis completed successfully!',
                'download_url': '/download'
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Analysis failed')
            }), 500
            
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 