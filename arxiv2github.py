import requests
import numpy as np

import sys
try:
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.pdfpage import PDFPage
    from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
    from pdfminer.layout import LAParams
except ImportError:
    raise ImportError('pdfminer is not installed. Install with pip install pdfminer.six')
import io

def _pdfparser(filename):
    ''' Parses a pdf into plain text string using pdfminer
    '''
    fp = open(filename, 'rb')
    rsrcmgr = PDFResourceManager()
    retstr = io.StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    # Create a PDF interpreter object.
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    # Process each page contained in the document.
    strs = []
    for idx, page in enumerate(PDFPage.get_pages(fp)):
        interpreter.process_page(page)
        strs.append(retstr.getvalue().replace('\n', ' '))
    return(' '.join(strs))


def arxiv2string(arxiv_id):
    ''' Download a pdf from arxiv and convert it into a plain text string
    '''
    url = 'https://arxiv.org/pdf/{}.pdf'.format(arxiv_id)
    response = requests.get(url)
    with open('/tmp/temparxiv.pdf', 'wb') as f:
        f.write(response.content)
    return _pdfparser('/tmp/temparxiv.pdf')


def search_in_string(string, search_term):
    ''' Given a string, will find the unique instances of `search_term` up to the nearest
        space or full stop.
    '''
    start = 0
    hit = np.nan
    matches = []
    while hit != -1:
        hit = string.find(search_term, start, len(string))
        endpoints = np.asarray([string.find(endpoint, hit + len(search_term), hit  + len(search_term) + 100) for endpoint in [' ', '.']])
        endpoints = endpoints[endpoints != -1]
        if len(endpoints) < 1:
            hit_end = len(string)
        else:
            hit_end = np.min(endpoints)
        matches.append(string[hit:hit_end])
        start = hit + len(search_term)
    matches = np.unique(np.asarray(matches))
    matches = matches[matches != '']
    return matches

def arxiv2github(arxiv_id):
    string = arxiv2string(arxiv_id)
    return search_in_string(string, 'github.com/')
