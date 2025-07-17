import glob
import os
import re

import ollama
import pdfplumber


def get_list_of_files(dirname, file_pattern):
    pattern = f"{dirname}/{file_pattern}*.pdf"
    list_of_pdfs = glob.glob(pattern)
    return list_of_pdfs


def main():
    file_list = get_list_of_files(
        os.environ.get("DIR_NAME"), os.environ.get("FILE_PATTERN")
    )
    for file in file_list:
        print(f"converting file {file}")
        convert_pdf(file)


def convert_pdf(filename):
    table_content = extract_table_content(filename)
    # print(f"Table contents: {table_content}")
    content = sanitize_content(table_content)
    # print(content)
    csv = convert_to_csv(content)
    save_csv(csv, filename)


def save_csv(csv, fullpath):
    fname, pdf_ext = os.path.basename(fullpath).split(".")
    directory = os.path.dirname(fullpath)
    csv_directory = os.path.join(directory, "csv")
    csv_file = os.path.join(csv_directory, fname + ".csv")
    if not os.path.exists(csv_directory):
        os.mkdir(csv_directory)
    with open(csv_file, "w") as file:
        file.write(csv)

    print(f"Success: file {csv_file} created successfully.")


def extract_csv(text):
    # Look for csv code block
    match = re.search(r"```csv\s*(.*?)\s*```", text)
    if match:
        return match.group(1).strip()
    # Fallback: remove leading lines like "Here is the..."
    lines = text.splitlines()
    csv_lines = [line for line in lines if "," in line]
    return "\n".join(csv_lines).strip()


def convert_to_csv(data):
    client = ollama.Client(host=os.environ.get("OLLAMA_SERVER"))
    response = client.chat(
        model="phi3:14b",
        messages=[
            {
                "role": "user",
                "content": f"convert this content to csv with date as the first column {data}. output should only contain csv data",
            }
        ],
    )
    csv_data = extract_csv(response.message.content)
    return csv_data


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
