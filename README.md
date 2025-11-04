# diagon-wise — Medical Report Analyzer

diagon-wise is a Flask web application that extracts text and structured laboratory results
from PDFs and images, then enriches those findings with AI-powered clinical summaries and
explanations. It's designed for quick local development inside GitHub Codespaces and simple
deployment workflows.

Key features
- OCR for PDFs and images
- Flexible extraction of lab test values and reference ranges
- AI-powered clinical summaries and per-test explanations
- Export results and AI summaries as a single PDF

Repository layout
- `app.py` — Flask application and routes
- `utils/` — helpers: `ocr.py`, `extract.py`, `summarizer.py`, `pdf_export.py`
- `templates/` and `static/` — front-end UI
- `tests/` — unit tests (pytest)
- `.env.example` — safe-to-commit example environment file

Quickstart (local development)
--------------------------------

Prerequisites
- Python 3.10+
- pip

Install and run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run the development server
flask --debug run
# Visit http://127.0.0.1:5000/ in your browser
```

Environment variables
---------------------
The application requires an AI API key. Do not commit real keys to the repository.

- `OPENROUTER_API_KEY` — API key for the OpenRouter-compatible AI service used by the
  summarizer and explanation flows.

Local testing (temporary)
-------------------------
For temporary testing you may export an env var in your shell session (do not commit):

```bash
export OPENROUTER_API_KEY="sk-..."
flask --debug run
```

Codespaces (recommended)
------------------------
To securely inject the key into Codespaces (preferred for developer convenience):

1. On GitHub, open your repository → Settings → Secrets and variables → Codespaces.
2. Choose "New repository secret" and add the name `OPENROUTER_API_KEY` with the key value.
3. Restart your Codespace so the secret is injected into the container environment.

GitHub Actions (CI)
--------------------
If workflows require the key, add it to Actions secrets:

1. Repo → Settings → Secrets and variables → Actions → New repository secret.
2. Name it `OPENROUTER_API_KEY` and paste the key.

In workflows you can access it as:

```yaml
env:
  OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
```

Health check and diagnostics
----------------------------
The app provides a minimal `/health` endpoint to verify AI authentication and readiness.
It returns a masked suffix of the configured API key so you can confirm the running process
has the expected secret without exposing it.

Example response:

```json
{
  "status": "ok",
  "ai_service_ok": true,
  "api_key_masked": "****61f8"
}
```

Testing
-------
Run unit tests with pytest:

```bash
pytest -q
```

Troubleshooting
---------------
- 401 Unauthorized from AI service: ensure `OPENROUTER_API_KEY` is set in the running process and has not been revoked. Restart the process after updating Codespaces secrets.
- No text extracted: try a higher-quality image/PDF or verify OCR dependencies are installed.

Security checklist
------------------
- Rotate API keys immediately if they are exposed.
- Never commit `.env` files with real secrets. Keep `.env` in `.gitignore` and use `.env.example` for documentation.
- Prefer repository Codespaces secrets and Actions secrets for CI rather than local files.

Contributing
------------
Contributions are welcome. Open an issue or a pull request. When adding features that require
new environment variables, update `.env.example` and `README.md` accordingly.

License
-------
This project is licensed under the MIT License. See `LICENSE` for details.