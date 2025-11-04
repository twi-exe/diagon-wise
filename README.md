# DiagonWise — AI-Powered Medical Report Analyzer

DiagonWise is a modern web application that helps users understand their medical lab reports through AI-powered analysis. Upload your PDF or image lab reports, and get instant insights with clear explanations of test results, reference ranges, and clinical summaries.

## 🌟 Features

- **Smart Document Processing**: Extracts text and structured data from PDFs and images using OCR
- **AI-Powered Analysis**: Leverages advanced AI to provide clinical summaries and explain test results in plain language
- **Visual Analytics**: Interactive charts showing test distributions, status breakdowns, and reference range comparisons
- **Privacy-Focused**: Files are processed temporarily and can be removed after analysis
- **Export Capabilities**: Download comprehensive PDF reports with AI summaries
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Secure & Local**: No data storage - analysis happens in your browser session

## 🔬 How It Works

1. **Upload**: Drag & drop or select your lab report (PDF or image format)
2. **Extract**: Advanced OCR extracts text and identifies test values, units, and reference ranges
3. **Analyze**: AI analyzes the data and generates clinical insights
4. **Visualize**: Interactive charts and tables display results with status indicators
5. **Export**: Download a professional PDF report for your records

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip (Python package manager)
- Git

### Local Development with Python/Flask

1. **Clone the repository**
   ```bash
   git clone https://github.com/twi-exe/diagon-wise.git
   cd diagon-wise
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENROUTER_API_KEY
   ```

5. **Run the development server**
   ```bash
   flask --debug run
   # Visit http://127.0.0.1:5000/ in your browser
   ```

### Production Deployment with Gunicorn

For production deployment, use Gunicorn as the WSGI server:

1. **Install Gunicorn**
   ```bash
   pip install gunicorn
   ```

2. **Run with Gunicorn**
   ```bash
   gunicorn --bind 0.0.0.0:8000 app:app
   # Access at http://localhost:8000
   ```

3. **Advanced Gunicorn configuration**
   ```bash
   gunicorn --workers 4 --bind 0.0.0.0:8000 --timeout 120 app:app
   ```

### Docker Deployment

Build and run with Docker:

1. **Build the Docker image**
   ```bash
   docker build -t diagon-wise .
   ```

2. **Run the container**
   ```bash
   docker run -p 5000:5000 --env-file .env diagon-wise
   # Access at http://localhost:5000
   ```

3. **Docker Compose (alternative)**
   ```yaml
   # docker-compose.yml
   version: '3.8'
   services:
     diagon-wise:
       build: .
       ports:
         - "5000:5000"
       env_file:
         - .env
   ```

   ```bash
   docker-compose up
   ```

## 🌐 Online Access

DiagonWise is deployed and accessible online at: **https://diagon-wise.onrender.com/**

The live deployment uses Render's free tier and may have cold start delays. For consistent performance, consider running locally or deploying to your preferred platform.

## 🔧 Environment Variables

The application requires an AI API key for analysis features:

- `OPENROUTER_API_KEY` — API key for OpenRouter-compatible AI service (required for AI summaries)

### Setting Environment Variables

**Local development:**
```bash
export OPENROUTER_API_KEY="your-api-key-here"
```

**Codespaces (recommended):**
1. Go to repository Settings → Secrets and variables → Codespaces
2. Add `OPENROUTER_API_KEY` as a repository secret
3. Restart your Codespace

**GitHub Actions:**
1. Repository Settings → Secrets and variables → Actions
2. Add `OPENROUTER_API_KEY` as a repository secret

## 🏥 Health Check

The app provides a `/health` endpoint to verify AI service connectivity:

```bash
curl https://diagon-wise.onrender.com/health
```

Response:
```json
{
  "status": "ok",
  "ai_service_ok": true,
  "api_key_masked": "****61f8"
}
```

## 🧪 Testing

Run the test suite with pytest:

```bash
pytest -q
```

### Docker Testing

To test the Docker build and deployment:

1. **Build the image**
   ```bash
   docker build -t diagon-wise:local .
   ```

2. **Run the container**
   ```bash
   docker run --rm -e OPENROUTER_API_KEY="$OPENROUTER_API_KEY" -p 5000:5000 diagon-wise:local
   ```

3. **Test health endpoint** (in another terminal)
   ```bash
   curl -sS http://127.0.0.1:5000/health | jq .
   ```

   Expected response:
   ```json
   {
     "status": "ok",
     "ai_service_ok": true,
     "api_key_masked": "****d084"
   }
   ```

4. **Test full app** (visit `http://127.0.0.1:5000` in browser and upload a test file)

## 🔒 Security & Privacy

- **No Data Storage**: Files are processed in memory and not stored permanently
- **Client-Side Processing**: Analysis happens on the server during your session
- **API Key Protection**: Keys are masked in logs and health checks
- **Secure Practices**: Follow security checklist for key management

## 🛠️ Repository Structure

```
diagon-wise/
├── app.py                 # Flask application and routes
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── pytest.ini           # Test configuration
├── utils/               # Helper modules
│   ├── ocr.py          # OCR text extraction
│   ├── extract.py      # Test data extraction
│   ├── summarizer.py   # AI analysis
│   └── pdf_export.py   # PDF generation
├── templates/          # Jinja2 templates
│   ├── DiagonWise.html # Main upload page
│   └── result.html     # Results display page
├── static/             # Static assets
│   └── style.css      # Stylesheet
├── tests/              # Unit tests
└── uploads/           # Temporary file storage
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

When adding new features that require environment variables, update `.env.example` and this README.

## 📄 License

This project is licensed under the MIT License. See `LICENSE` for details.

## ⚠️ Disclaimer

DiagonWise is for informational purposes only and should not replace professional medical advice. Always consult with qualified healthcare providers for medical decisions and interpretation of lab results.