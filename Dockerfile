FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       gcc \
       libffi-dev \
       libpq-dev \
       libcairo2 \
       libpango-1.0-0 \
       libpangoft2-1.0-0 \
       libgdk-pixbuf-xlib-2.0-0 \
       libgobject-2.0-0 \
       libxml2 \
       libxslt1.1 \
       tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*WORKDIR /app

# Install runtime dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Expose port
EXPOSE 5000

# Use gunicorn for production
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "60"]
