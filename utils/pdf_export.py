from fpdf import FPDF
import tempfile

def generate_pdf(tests, summary):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.set_font(style='B')
    pdf.cell(200, 10, "Medical Report Summary", ln=True, align="C")
    pdf.set_font(style='')

    pdf.ln(10)
    pdf.set_font(size=11)
    pdf.cell(200, 10, "Abnormality Table:", ln=True)
    pdf.ln(5)

    for t in tests:
        pdf.multi_cell(0, 8,
            f"{t['test']}: {t['value']} {t['unit']} (Ref: {t['ref_range']})\n"
            f"Status: {t['status']} | Explanation: {t['explanation']}\n", border=1)

    pdf.ln(10)
    pdf.set_font(style='B')
    pdf.cell(200, 10, "AI Summary:", ln=True)
    pdf.set_font(style='')
    pdf.multi_cell(0, 10, summary)

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp_file.name)
    return tmp_file.name
