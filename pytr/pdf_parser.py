import glob
import os
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path

import pdfplumber

crypto_isin = {
    "Bitcoin (BTC)": "XF000BTC0017",
    "Ethereum (ETH)": "XF000ETH0019",
    "Solana (SOL)": "XF000SOL0012"
}


@dataclass
class Trade:
    trade_date: str
    order_type: str  # SELL or BUY
    stock_name: str
    amount: float
    item_price: float
    currency: str
    total_price: float
    stock_id: str = field(default=None)


def parse_folder(pdf_folder):
    glob_pattern = f"{pdf_folder}/**/*.pdf"
    files_glob = glob.glob(glob_pattern, recursive=True)
    for i, filename in enumerate(files_glob, start=1):
        parse_file(filename)


def parse_order_type(line):
    order_line = str.lower(line)
    if "verkauf" in order_line or "sell" in order_line:
        return "SELL"
    elif "kauf" in order_line or "buy" in order_line or "spar" in order_line:
        return "BUY"
    else:
        raise ValueError(f"Unable to parse order type: {line}")


def parse_file(pdf_file_location):
    output_fields = 'trade_date;order_type;stock_id;stock_name;amount;item_price;total_price'.split(";")

    basename, suffix = os.path.splitext(os.path.basename(pdf_file_location))
    trade_date = basename[:len("YYYY-MM-DD")]

    with pdfplumber.open(pdf_file_location) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            lines = text.splitlines()
            # print(text)

        for line_no, line in enumerate(lines):
            if line == "ÜBERSICHT":
                order_type = parse_order_type(lines[line_no + 1])

            if line in ['POSITION ANZAHL PREIS BETRAG', 'POSITION ANZAHL DURCHSCHNITTSKURS BETRAG']:
                trade_line = lines[line_no + 1]
                trade_split = trade_line.split(" ")
                stock_name_parts = []
                for cell_no, trade_cell in enumerate(trade_split):
                    if not trade_cell.startswith("Stk"):
                        stock_name_parts.append(trade_cell)
                    else:
                        stock_name = " ".join(stock_name_parts[:-1])
                        trade_split = [stock_name] + trade_split[cell_no - 1:]
                        break
                trade = Trade(trade_date=trade_date, order_type=order_type,
                              stock_name=trade_split[0], amount=trade_split[1], item_price=trade_split[3],
                              currency=trade_split[4], total_price=trade_split[5])
                isin_line = lines[line_no + 2]
                if "ISIN: " in isin_line:
                    isin = isin_line.split(":")[-1].strip()
                    # trade_split.append(isin)
                    trade.stock_id = isin
                elif trade_split[0] in crypto_isin.keys():
                    isin = crypto_isin.get(trade_split[0])
                    # trade_split.append(isin)
                    trade.stock_id = isin
                # print(f"{trade_line} --> {trade_split}")
                # print(";".join(trade_split))

                trade_dict = asdict(trade)
                trade_csv = ";".join([trade_dict.get(f) for f in output_fields])
                print(trade_csv)


if __name__ == '__main__':
    pdf_file_name = sys.argv[1]
    home_dir = Path.home()
    tr_doc_dir = f"{home_dir}/Dokumente/traderepublic"
    # parse_file(f"{tr_doc_dir}/Abrechnung/{pdf_file_name}")

    parse_folder(f"{tr_doc_dir}/Abrechnung") # käufe
    parse_folder(f"{tr_doc_dir}/Sparplan/Abrechnung Ausführung")  # crypto sparpläne

    # parse_folder(f"{tr_doc_dir}/Abrechnung Ausführung") # aktien sparpläne --> anderes format
