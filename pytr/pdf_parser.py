import glob
import sys
from pathlib import Path

import pdfplumber

def parse_folder(pdf_folder):
    glob_pattern = f"{pdf_folder}/**/*.pdf"
    files_glob = glob.glob(glob_pattern, recursive=True)
    for i, filename in enumerate(files_glob, start=1):
        print(filename)

def parse_file(pdf_file_location):
    with pdfplumber.open(pdf_file_location) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            lines = text.splitlines()
            #print(text)

        for line_no, line in enumerate(lines):
            if line == 'POSITION ANZAHL PREIS BETRAG':
                trade_line = lines[line_no + 1]
                trade = trade_line.split(" ")
                isin_line =  lines[line_no + 2]
                print(f"f{trade_line} --> {trade}")
                print(isin_line)

if __name__ == '__main__':
    pdf_file_name = sys.argv[1]
    home_dir = Path.home()
    tr_doc_dir = f"{home_dir}/Dokumente/traderepublic"
    parse_file(f"{tr_doc_dir}/Abrechnung/{pdf_file_name}")
    #parse_folder(f"{tr_doc_dir}/Abrechnung") # käufe
    #parse_folder(f"{tr_doc_dir}/Abrechnung Ausführung") # aktien sparpläne
    #parse_folder(f"{tr_doc_dir}/Abrechnung Ausführung") # crypto sparpläne