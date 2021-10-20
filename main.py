from markdowngenerator import MarkdownGenerator
from typing import List
import os
import pyodbc
import sys

VP = True

def main() -> None:
    # Find database
    db_file = "database.accdb"
    if len(sys.argv) > 1:
        db_file = sys.argv[1]

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

    if VP:
        cursor.execute("SELECT * from SystemRequirement")
        results = cursor.fetchall()
        packages = set(result.cmbVerificationPackage for result in results)
        packages = sorted(x for x in packages if x != None and x != "")
        for package_name in packages:
            filename = os.path.join("verification-packages", f"{package_name} Package.md")
            with MarkdownGenerator(
                filename=filename,
                enable_TOC=False,
                enable_write=False,
            ) as doc:
                doc.addHeader(1, f"Package for {package_name}")
                generate_vp(cursor, doc, results, package_name)
    else:
        # Now that you're connected to the database, let's make a spec based on a component
        # for rows in cursor.execute("SELECT "):
        cursor.execute("SELECT * FROM SystemRequirement where Number NOT LIKE '_.%'")
        for row in cursor.fetchall():
            filename = os.path.join("md-specs", f"{row.Name} Specification.md")
            with MarkdownGenerator(
                filename=filename,
                enable_TOC=False,
                enable_write=False,
            ) as doc:
                doc.addHeader(1, f"Specification for {row.Name}")
                generate_spec(cursor, doc, row.Number)
    print("Finished")
    return


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


def generate_vp(
    cursor: pyodbc.Cursor,
    doc: MarkdownGenerator,
    all_packages: list,
    package_name: str,
) -> None:
    print(f"{package_name = }")
    packages = [package for package in all_packages if package.cmbVerificationPackage == package_name]
    packages.sort(key=lambda package: package.Number)
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


def get_system_name(all_packages: list, package_number: int) -> str:
    package_number = str(package_number)
    for package in all_packages:
        if package.Number == package_number:
            return package.Name
    return None


if __name__ == "__main__":
    main()
