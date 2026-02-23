from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

def generate_pdf(filename, text):
    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("AI Data Analysis Report", styles["Heading1"]))
    elements.append(Spacer(1, 0.5 * inch))
    elements.append(Paragraph(text.replace("\n", "<br/>"), styles["Normal"]))

    doc.build(elements)