# app.py (Final working version with safe JSON handling for PDF download)
import os
import json
from flask import Flask, render_template, request, send_file
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

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files.get('report')
        if not f:
            return render_template('index.html', error="No file uploaded.")

        try:
            filename = secure_filename(f.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            f.save(file_path)

            # Extract text
            if filename.lower().endswith('.pdf'):
                text = extract_text_from_pdf(file_path)
            else:
                text = extract_text_from_image(file_path)

            # Extract abnormalities
            tests = extract_tests(text)

            # Generate summary from raw text
            try:
                summary = generate_summary(text)
            except Exception as e:
                summary = f"Error generating summary: {str(e)}"

            return render_template(
                'result.html',
                original=text,
                summary=summary,
                tests=tests,
                tests_json=json.dumps(tests)
            )

        except Exception as e:
            return render_template('index.html', error=f"Unexpected error: {str(e)}")

    return render_template('index.html')


@app.route('/download', methods=['POST'])
def download_pdf():
    summary_html = request.form.get('summary', '')
    pdf_path = generate_pdf_from_html(summary_html)
    return send_file(pdf_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

