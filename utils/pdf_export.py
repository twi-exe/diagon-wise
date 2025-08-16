from weasyprint import HTML
import tempfile
import os

def generate_pdf_from_html(html_content):
    # Wrap the content in a full HTML document
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Arial', sans-serif; font-size: 12px; padding: 20px; }}
            h3 {{ color: #1f4e79; }}
            span[style*='color: red'] {{ color: red; font-weight: bold; }}
            ul {{ margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    HTML(string=full_html).write_pdf(tmp_file.name)
    return tmp_file.name
