import os
from flask import Flask, render_template, request, send_file
from dotenv import load_dotenv
from utils.ocr import extract_text_from_pdf, extract_text_from_image
from utils.extract import extract_tests
from utils.summarizer import generate_summary
from utils.pdf_export import generate_pdf
import tempfile

load_dotenv()
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['report']
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f.filename)
        f.save(file_path)

        if f.filename.lower().endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
        else:
            text = extract_text_from_image(file_path)

        tests = extract_tests(text)
        summary = generate_summary(text)

        return render_template('result.html', original=text, summary=summary, tests=tests)

    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_pdf():
    summary = request.form['summary']
    tests_data = eval(request.form['tests'])  # Use json.loads in production
    pdf_path = generate_pdf(tests_data, summary)
    return send_file(pdf_path, as_attachment=True)
