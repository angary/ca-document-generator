import argparse
import markdown
import os
import pdfkit
import pyodbc
import sys

from markdowngenerator import MarkdownGenerator
from pygments import highlight
from pygments.formatters import HtmlFormatter
from typing import List


def main() -> None:
    # Find database
    args = parse_args()
    db_file = args.db_file
    vp = args.verification_package
    pdf = args.pdf

    # Connect to the database file
    try:
        conn = pyodbc.connect(
            r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};" +
            f"Dbq={os.path.join(os.getcwd(), db_file)}"
        )
        cursor = conn.cursor()
        print(f"Connected {db_file}")

    except pyodbc.Error as e:
        sys.exit(f"Error in Connection {e}")

    files = []
    if vp:
        files = generate_all_vp(cursor)
    else:
        files = generate_all_spec(cursor)
    
    if pdf:
        gen_pdfs(files)
    print("Finished")
    return


def generate_all_spec(cursor: pyodbc.Cursor) -> List[str]:
    file_paths = []
    cursor.execute("SELECT * FROM SystemRequirement where Number NOT LIKE '_.%'")
    for row in cursor.fetchall():
        filename = os.path.join("md-specs", f"{row.Name} Specification.md")
        file_paths.append(filename)
        with MarkdownGenerator(
            filename=filename,
            enable_TOC=False,
            enable_write=False,
        ) as doc:
            doc.addHeader(1, f"Specification for {row.Name}")
            generate_spec(cursor, doc, row.Number)
    return file_paths


def generate_spec(
    cursor: pyodbc.Cursor,
    doc: MarkdownGenerator,
    number: str
) -> None:
    print(number)
    cursor.execute("SELECT * from SystemRequirement where Number LIKE '{number}.%'")
    for row in cursor.fetchall():
        doc.addHeader(2, f"{row.Number} {row.Name}")
        table = [{
            "Description": row.Description.replace("\r", " ").replace("\n", " "),
            "Priority": row.cmbPriority,
            "Verification Status": row.cmbVerificationStatus
        }]
        doc.addTable(dictionary_list=table)
    return


def generate_all_vp(cursor: pyodbc.Cursor) -> List[str]:
    file_paths = []
    cursor.execute("SELECT * from SystemRequirement")
    results = cursor.fetchall()
    packages = set(result.cmbVerificationPackage for result in results)
    packages = sorted(p for p in packages if p != None and p != "")
    for package_name in packages:
        filename = os.path.join("verification-packages", f"{package_name} Package.md")
        file_paths.append(filename)
        with MarkdownGenerator(
            filename=filename,
            enable_TOC=False,
            enable_write=False,
        ) as doc:
            doc.addHeader(1, f"Package for {package_name}")
            generate_vp(cursor, doc, results, package_name)
    return file_paths


def generate_vp(
    cursor: pyodbc.Cursor,
    doc: MarkdownGenerator,
    all_packages: List[pyodbc.Row],
    package_name: str,
) -> None:
    print(f"Converting {package_name}")
    packages = [p for p in all_packages if p.cmbVerificationPackage == package_name]
    packages.sort(key=lambda p: p.Number)
    prev_system = -1
    for row in packages:
        curr_system = int(row.Number[0])
        if curr_system != prev_system:
            prev_system = curr_system
            system_name = get_system_name(all_packages, curr_system)
            doc.addHeader(2, system_name)
        doc.addHeader(3, f"{row.Number} {row.Name}")
        table = [{
            "Description": row.Description.replace("\r", " ").replace("\n", " "),
            "Priority": row.cmbPriority,
            "Verification Status": row.cmbVerificationStatus
        }]
        doc.addTable(dictionary_list=table)
    return


def get_system_name(all_packages: List[pyodbc.Row], package_number: int) -> str:
    package_number = str(package_number)
    for package in all_packages:
        if package.Number == package_number:
            return package.Name
    return None


def gen_pdfs(file_paths: List[str]) -> None:
    for md_file_path in file_paths:
        print(f"Generating pdf for {md_file_path}")
        html = ""
        with open(md_file_path, mode="r", encoding="UTF-8") as f:
            text = f.read()
            # Create stylesheets for highlights with Pygments
            style = HtmlFormatter(style="solarized-dark").get_style_defs(".codehilite")
            # Markdown -> HTML conversion
            md = markdown.Markdown(extensions=["extra", "codehilite"])
            body = md.convert(text)
            # Fit to HTML format
            html = '<html lang="en"><meta charset="utf-8"><body>'
            # Import stylesheets created with Pygments
            html += f"<style>{style}</style>"
            # Add style to add border to Table tag
            html += """
                <style> 
                    * {
                        font-family: Arial, Helvetica, sans-serif;
                    }
                    table,th,td {
                        width: 100%;
                        border-collapse: collapse;
                        border:1px solid #333;
                        padding: 5px;
                    } 
                </style>
            """
            html += body + "</body></html>"
        
        pdf_file_path = md_file_path.replace(".md", ".pdf")
        path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
        config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
        pdfkit.from_string(html, pdf_file_path, configuration=config)
        print()
    return


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "db_file",
        type=str,
        nargs="?",
        default="database.accdb",
        help="the path to the database file"
    )
    parser.add_argument(
        "-p",
        "--pdf",
        action="store_true",
        help="create pdf versions alongside the markdown files"
    )
    parser.add_argument(
        "-vp",
        "--verification-package",
        action="store_true",
        help="create documentation for the verification packages"
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
