from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine
import PyPDF2

class pdf_to_text():
    """Converts pdf to text with pdfminer"""
    def __init__(self):
        pass
        
    def convert_pdfminer(self, fname):
        fp = open(fname, 'rb')
        parser = PDFParser(fp)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        text = ''
        for page in PDFPage.create_pages(doc):
            interpreter.process_page(page)
            layout = device.get_result()
            for lt_obj in layout:
                if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
                    text += lt_obj.get_text()
        return text

    def convert_PyPDF2(self,fname):
        pdfFileObj = open(fname,'rb')
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
        text = ''
        for i in range(pdfReader.numPages):
            pageObj = pdfReader.getPage(i)
            text += pageObj.extractText()
        return text

if __name__ == '__main__':
    pass