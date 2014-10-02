#!/bin/bash/python3.4

from datetime import datetime
import csv
import sys

CSV_HEADER_LINE_INDEX = 6


def reformat_row(row):
    fixed_row = row
    fixed_row.pop("Valutadatum", None)
    fixed_row.pop("Saldo", None)

    # Reformat date to US format
    try:
        timestamp = datetime.strptime(fixed_row["Buchungsdatum"],
                                      "%d.%m.%Y")
        fixed_row["Buchungsdatum"] = timestamp.strftime("%d/%m/%Y")
    except ValueError:
        return {}

    # Reformat "Text" field by splitting it into lines
    # to get Payee/Category/Memo.
    is_outflowing = (fixed_row["Gutschrift"] == "")
    if not is_outflowing:
        fixed_row["Payee"] = "Myself"

    split_text = fixed_row["Text"].split(',')
    formatted_text = []
    for line in split_text:
        formatted_text.append(line.strip())
    fixed_row["Text"] = ', '.join(formatted_text)

    # Gather category according to filters:
    if "Bezug" in formatted_text[0]:
        fixed_row["Category"] = "Cash withdrawal"

    return fixed_row


def main(file_name):
    csv_file = open(file_name, 'r')
    csv_reader = csv.reader(csv_file)

    field_names = []
    i = 0
    for row in csv_reader:
        if i == CSV_HEADER_LINE_INDEX:
            field_names = row
            break
        else:
            i = i + 1

    csv_dict_reader = csv.DictReader(csv_file, field_names)

    output_order_dict = ["Buchungsdatum", "Payee", "Category", "Text",
                         "Belastung", "Gutschrift"]

    out_file = open('out.csv', 'w')
    csv_dict_writer = csv.DictWriter(out_file, output_order_dict)

    out_file.write("Date,Payee,Category,Memo,Outflow,Inflow\n")

    for row in csv_dict_reader:
        csv_dict_writer.writerow(reformat_row(row))

    csv_file.close()
    out_file.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(1)
    main(sys.argv[1])
