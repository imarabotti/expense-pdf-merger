from PyPDF2 import PdfFileMerger, PdfFileReader

filenames = [
    './generica.pdf',
    './accountstatus.pdf'
]

merger = PdfFileMerger()
for filename in filenames:
    merger.append(PdfFileReader(open(filename, 'rb')))

merger.write("merged.pdf")