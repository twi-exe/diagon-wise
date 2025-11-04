# app.py (Updated to always generate AI results)
import os
import json
import requests
from flask import Flask, render_template, request, send_file, jsonify
from dotenv import load_dotenv
from utils.ocr import extract_text_from_pdf, extract_text_from_image
from utils.extract import extract_tests
from utils.summarizer import generate_summary
from utils.pdf_export import generate_pdf_from_html
from werkzeug.utils import secure_filename

load_dotenv()
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# AI service health status (set on first request)
app.config['AI_SERVICE_OK'] = None


def _mask_key(val: str) -> str:
    if not val:
        return None
    return f"****{val[-4:]}"


def check_ai_service():
    """Lightweight check to verify OpenRouter auth without leaking tokens.

    This will perform a minimal POST with a small max_tokens and set
    app.config['AI_SERVICE_OK'] = True/False depending on the status.
    """
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        app.logger.warning("OPENROUTER_API_KEY not set in environment")
        app.config['AI_SERVICE_OK'] = False
        return False

    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistralai/mixtral-8x7b-instruct",
                "messages": [{"role": "user", "content": "auth check"}],
                "max_tokens": 1
            },
            timeout=5
        )
        if resp.status_code == 200:
            app.logger.info("AI auth check succeeded")
            app.config['AI_SERVICE_OK'] = True
            return True
        else:
            app.logger.warning(f"AI auth check failed: {resp.status_code} {resp.text}")
            app.config['AI_SERVICE_OK'] = False
            return False

    except Exception as e:
        app.logger.warning(f"AI auth check error: {e}")
        app.config['AI_SERVICE_OK'] = False
        return False


@app.route('/health', methods=['GET'])
def health():
    # Ensure we run the check at least once
    if app.config.get('AI_SERVICE_OK') is None:
        check_ai_service()
    return jsonify({
        'status': 'ok',
        'ai_service_ok': bool(app.config.get('AI_SERVICE_OK')),
        'api_key_masked': _mask_key(os.getenv('OPENROUTER_API_KEY'))
    })

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files.get('report')
        if not f:
            return render_template('DiagonWise.html', error="No file uploaded.")

        try:
            filename = secure_filename(f.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            f.save(file_path)

            # Extract text
            if filename.lower().endswith('.pdf'):
                text = extract_text_from_pdf(file_path)
            else:
                text = extract_text_from_image(file_path)

            # Check if we have any text at all
            if not text or len(text.strip()) < 10:
                return render_template('DiagonWise.html', error="Could not extract readable text from the document. Please try a clearer image or PDF.")

            # Try to extract structured test data
            tests = extract_tests(text)
            
            # Debug output
            print(f"Extracted text length: {len(text)}")
            print(f"Found {len(tests)} structured tests")
            for i, test in enumerate(tests):
                print(f"  Test {i+1}: {test['test']} = {test['value']} {test['unit']} ({test['status']})")
            
            # ALWAYS generate AI summary regardless of structured data
            try:
                summary = generate_summary(text)
                print("AI summary generated successfully")
            except Exception as e:
                print(f"AI summary generation failed: {str(e)}")
                # Provide a fallback summary
                summary = f"""
                <h3>Document Analysis</h3>
                <ul>
                    <li>Successfully extracted text from your medical document</li>
                    <li>Document contains {len(text)} characters of content</li>
                    {'<li><b>Found ' + str(len(tests)) + ' structured test results</b></li>' if tests else '<li>No structured test tables detected</li>'}
                </ul>
                <h3>Next Steps</h3>
                <ul>
                    <li>Review the extracted content below</li>
                    <li>Consult with your healthcare provider for professional interpretation</li>
                    <li>Keep this document for your medical records</li>
                </ul>
                <p><small>Note: AI analysis temporarily unavailable. Error: {str(e)}</small></p>
                """

            # Always return results - either with or without structured data
            return render_template(
                'result.html',
                original=text,
                summary=summary,
                tests=tests,
                tests_json=json.dumps(tests),
                ai_only=(len(tests) == 0),
                has_structured_data=(len(tests) > 0)
            )

        except Exception as e:
            print(f"Error processing file: {str(e)}")
            return render_template('DiagonWise.html', error=f"Error processing file: {str(e)}")

    return render_template('DiagonWise.html')


@app.route('/download', methods=['POST'])
def download_pdf():
    summary_html = request.form.get('summary', '')
    tests_json = request.form.get('tests', '[]')
    
    # Create comprehensive HTML for PDF
    try:
        tests = json.loads(tests_json) if tests_json else []
    except:
        tests = []
    
    # Generate enhanced HTML for PDF export
    pdf_html = f"""
    <h1>Medical Report Analysis</h1>
    
    <h2>AI Analysis Summary</h2>
    {summary_html}
    
    {f'''
    <h2>Structured Test Results</h2>
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <tr>
            <th>Test</th>
            <th>Value</th>
            <th>Reference Range</th>
            <th>Status</th>
            <th>Explanation</th>
        </tr>
        {"".join([f"<tr><td>{test.get('test', '')}</td><td>{test.get('value', '')} {test.get('unit', '')}</td><td>{test.get('ref_range', '')}</td><td>{test.get('status', '')}</td><td>{test.get('explanation', '')}</td></tr>" for test in tests])}
    </table>
    ''' if tests else ''}
    
    <p><small>Generated by Medical Report Analyzer - For informational purposes only. Consult healthcare provider for medical advice.</small></p>
    """
    
    pdf_path = generate_pdf_from_html(pdf_html)
    return send_file(pdf_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

