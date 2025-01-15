from fpdf import FPDF

async def create_pdf(content: str, file_path: str):
    """
    Создаёт PDF-файл из текста.
    """

    pdf = FPDF()
    pdf.add_page()

    font_path = "fonts/Roboto.ttf"

    pdf.add_font('Roboto', '', font_path, uni=True)
    pdf.set_font("Roboto", size=12)

    # Резделяем текст на строки для добавления в PDF
    for line in content.split("\n"):
        pdf.multi_cell(190, 6, line)
    
    pdf.output(file_path)