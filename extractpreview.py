#!/usr/bin/env python
import argparse
from io import StringIO
import os
import sys

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.utils import open_filename


from ricecooker_utils_pdf import PDFParser as RicecookerPDFParser
from PyPDF2 import PdfFileWriter


# TOC EXTRACTION
################################################################################

class PDFParser(RicecookerPDFParser):

    def write_page_numbers(self, page_numbers, outfilepath):
        """
        Save the pages specified in `page_numbers` (list) to `outfilepath`.
        """
        writer = PdfFileWriter()
        for page_number in page_numbers:
            writer.addPage(self.pdf.getPage(page_number))
            writer.removeLinks()
        with open(outfilepath, 'wb') as outfile:
            writer.write(outfile)



# PAGE TEXT EXTRACTION
################################################################################

def extract_text_by_page(pdf_file, password='', page_numbers=None, maxpages=0,
                         caching=True, codec='utf-8', laparams=None):
    """
    Parse and return the text contained in each page of a PDF file. Taken from
    https://github.com/pdfminer/pdfminer.six/blob/master/pdfminer/high_level.py#L90-L123
    and adapted to return the text of each page separately as a dictionary obj.
    :param pdf_file: Either a file path or a file-like object for the PDF file
        to be worked on.
    :param password: For encrypted PDFs, the password to decrypt.
    :param page_numbers: List of zero-indexed page numbers to extract.
    :param maxpages: The maximum number of pages to parse
    :param caching: If resources should be cached
    :param codec: Text decoding codec
    :param laparams: An LAParams object from pdfminer.layout. If None, uses
        some default settings that often work well.
    :return: a dict containing the text from each page (keys = page numbers)
    """
    if laparams is None:
        laparams = LAParams()

    text_by_page = {}

    with open_filename(pdf_file, "rb") as fp:
        rsrcmgr = PDFResourceManager()
        pages_iterable = PDFPage.get_pages(fp, page_numbers, maxpages=maxpages, password=password, caching=caching)
        if page_numbers is None:
            tuples_iterable = enumerate(pages_iterable)
        else:
            tuples_iterable = zip(page_numbers, pages_iterable)
        for page_num, page in tuples_iterable:
            # print('Processing page_num', page_num)
            with StringIO() as output_string:
                device = TextConverter(rsrcmgr, output_string, codec=codec, laparams=laparams)
                interpreter = PDFPageInterpreter(rsrcmgr, device)
                interpreter.process_page(page)
                text_by_page[page_num] = output_string.getvalue()
    return text_by_page





# CLI
################################################################################

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Book preview generator.')
    parser.add_argument('bookpath', help='source file')
    parser.add_argument('previewpath', nargs='?', help='destination for preview file')
    parser.add_argument('-p', '--pagerange', action='append', help="page range")
    parser.add_argument('--spec', help='preview spec file (JSON)')
    parser.add_argument('--printtoc', action='store_true', help='print the TOC')
    args = parser.parse_args()


    # debug info
    if args.printtoc:
        print('Loading TOC from book file', args.bookpath)
        with PDFParser(args.bookpath) as pdfparser:
            last_page_zerobased = pdfparser.pdf.numPages - 1
            full_toc = pdfparser.get_toc(subchapters=True)        
            for ch in full_toc:
                ch_start_onebased = str(ch['page_start']+1)
                ch_end_onebased = str(min(ch['page_end'], last_page_zerobased)+1)
                ch_range_onebased = ch_start_onebased+'-'+ch_end_onebased
                print( ' -', ch['title'], '  --pagerange',  '"' + ch_range_onebased +'"')
                if 'children' in ch:
                    for sec in ch['children']:
                        sec_start_onebased = str(sec['page_start']+1)
                        sec_end_onebased = str(min(sec['page_end'], last_page_zerobased)+1)
                        sec_range_onebased = sec_start_onebased + '-' + sec_end_onebased
                        print( '   -', sec['title'], '  --pagerange',  '"' + sec_range_onebased +'"')
        sys.exit(0)

    # set default output path
    if args.previewpath is None:
        filepath_noext, ext = os.path.splitext(args.bookpath)
        args.previewpath = filepath_noext + '_preview' + ext

    if args.pagerange:
        page_numbers_onebased_set = set()
        for pagerange in args.pagerange:
            chunks = pagerange.split(',')
            for chunk in chunks:
                if '-' in chunk:
                    start_str, end_str = chunk.split('-')
                    start, end = int(start_str), int(end_str)
                    page_numbers_onebased_set = page_numbers_onebased_set.union(range(start,end+1))
                else:
                    page_num_onebased = int(chunk)
                    page_numbers_onebased_set.add(page_num_onebased)
            # convert to 0-based indexing
            page_numbers = [n-1 for n in sorted(page_numbers_onebased_set)]
    else:
        print('Missing --pagerange input; defaulting to show first 20 pages.')
        page_numbers = range(0, 20)

    with PDFParser(args.bookpath) as pdfparser:
        pdfparser.write_page_numbers(page_numbers, args.previewpath)
        print('Preview written to', args.previewpath)
