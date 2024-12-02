from fpdf import FPDF

pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_font("Arial", size=12)

pdf.set_font("Arial", style='B', size=14)
pdf.cell(0, 10, "Generated PDF of Conversation", ln=True, align='C')
pdf.ln(10)

file_path = "Generated_Conversation.pdf"
pdf.output(file_path)