from markdowngenerator import MarkdownGenerator
from typing import List
import os
import pyodbc
import sys


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
    cursor.execute(f"SELECT * from SystemRequirement where Number LIKE '{number}.%'")
    for row in cursor.fetchall():
        doc.addHeader(2, f"{row.Number} {row.Name}")
        table = [{
            "Description": row.Description.replace("\r", " ").replace("\n", " "),
            "Priority": row.cmbPriority,
            "Verification Status": row.cmbVerificationStatus
        }]
        doc.addTable(dictionary_list=table)
    return


if __name__ == "__main__":
    main()
