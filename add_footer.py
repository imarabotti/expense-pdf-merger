from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
from pdfrw import PdfReader
from pdfrw.toreportlab import makerl
from pdfrw.buildxobj import pagexobj

def add_footer():
    input_file = "/tmp/merged.pdf"
    output_file = "/tmp/merged_footer.pdf"

    # Get pages
    reader = PdfReader(input_file)
    pages = [pagexobj(p) for p in reader.pages]

    # Compose new pdf
    canvas = Canvas(output_file)

    for page_num, page in enumerate(pages, start=1):

        # # Add page
        canvas.setPageSize((page.BBox[2], page.BBox[3]))
        canvas.doForm(makerl(canvas, page))

        canvas.setFont("Helvetica", 10)

        if canvas._pagesize[0] > canvas._pagesize[1]:
            canvas.saveState()
            canvas.rotate(270)
            canvas.translate(-30, -A4[0] + 30)
            canvas.drawRightString(-10, A4[0], "%d de %d" % (canvas._pageNumber, len(pages)))
            canvas.restoreState()
        else:
            canvas.drawRightString(A4[0] - 60, 30, "%d de %d" % (canvas._pageNumber, len(pages)))

        canvas.showPage()

    canvas.save()