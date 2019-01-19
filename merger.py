from PyPDF2 import PdfFileMerger, PdfFileReader

def merge_pdfs():
    filenames = [ "/tmp/expense.pdf", "/tmp/account-status.pdf" ]

    merger = PdfFileMerger()
    for filename in filenames:
        merger.append(PdfFileReader(open(filename, 'rb')))

    merger.write("/tmp/merged.pdf")