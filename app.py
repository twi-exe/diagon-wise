import os
import logging
from flask import Flask, render_template, request
from dotenv import load_dotenv
from utils.ocr import extract_text_from_pdf, extract_text_from_image
from utils.summarizer import generate_summary

load_dotenv()

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

logging.basicConfig(filename='logs/app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['report']
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f.filename)
        f.save(file_path)

        try:
            if f.filename.lower().endswith('.pdf'):
                text = extract_text_from_pdf(file_path)
            else:
                text = extract_text_from_image(file_path)

            summary = generate_summary(text)

            return render_template("result.html", original=text, summary=summary)
        except Exception as e:
            logging.error("Error: %s", str(e))
            return "Error occurred. Check logs."

    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
