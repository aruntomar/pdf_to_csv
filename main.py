import os

import pdfplumber


def main():
    filename = os.environ.get("FILE_NAME")
    table_content = extract_table_content(filename)
    # print(f"Table contents: {table_content}")
    content = sanitize_content(table_content)
    print(content)


def extract_table_content(filename):
    pdf = pdfplumber.open(filename)
    page = pdf.pages[0]
    table_content = page.extract_table()
    return table_content


def sanitize_content(raw_table):
    columns = ["Description", "Debit", "Credit", "Date", "Balance"]

    cleaned_rows = []
    for row in raw_table:
        # print(f"Row: {row}")
        if not row or all(cell in ("", None) for cell in row):
            continue
        if row[0] and "CHQ ENCLOSED" in row[0]:
            break  # Reached footer section

        if row[0] == "DESCRIPTION":
            continue  # Skip header row

        entry = dict(zip(columns, row[:5]))
        # print(f"Entry: {entry}")
        cleaned_rows.append(entry)

    return cleaned_rows


if __name__ == "__main__":
    main()
